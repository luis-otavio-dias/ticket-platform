"""Tests for the auth endpoints of the user app."""

from http import HTTPStatus

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User

REGISTER_URL = "/api/auth/register/"
PASSWORD = "S3cure-Passw0rd!"


@pytest.mark.django_db
def test_register_customer_sets_cookies_and_returns_user() -> None:
    client = APIClient()
    payload = {
        "email": "customer@example.com",
        "name": "Carol",
        "password": PASSWORD,
        "role": "CUSTOMER",
    }

    response = client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["user"]["email"] == "customer@example.com"
    assert response.json()["user"]["role"] == "CUSTOMER"

    assert "access" not in response.json()
    assert "refresh" not in response.json()

    access_cookie = response.cookies["access_token"]
    refresh_cookie = response.cookies["refresh_token"]
    assert access_cookie["httponly"]
    assert refresh_cookie["httponly"]

    user = User.objects.get(email="customer@example.com")
    assert user.check_password(PASSWORD)


@pytest.mark.django_db
def test_register_duplicate_email_returns_400() -> None:
    client = APIClient()
    payload = {
        "email": "dupe@example.com",
        "name": "D",
        "password": PASSWORD,
        "role": "CUSTOMER",
    }
    first = client.post(REGISTER_URL, payload, format="json")
    assert first.status_code == HTTPStatus.CREATED

    response = client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "email" in response.json()


@pytest.mark.django_db
def test_register_weak_password_returns_400() -> None:
    client = APIClient()
    payload = {
        "email": "weak@example.com",
        "name": "W",
        "password": "password",
        "role": "CUSTOMER",
    }

    response = client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "password" in response.json()


@pytest.mark.django_db
def test_anonymous_cannot_register_receptionist() -> None:
    client = APIClient()
    payload = {
        "email": "gate@example.com",
        "name": "G",
        "password": PASSWORD,
        "role": "RECEPTIONIST",
    }

    response = client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == HTTPStatus.FORBIDDEN


def _client_with_access_token(user: User) -> APIClient:
    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.cookies["access_token"] = str(refresh.access_token)
    return client


def _organizer_client(email: str) -> APIClient:
    organizer = User.objects.create_user(
        email=email,
        password=PASSWORD,
        role=User.Role.ORGANIZER,
    )
    return _client_with_access_token(organizer)


@pytest.mark.django_db
def test_organizer_can_register_receptionist() -> None:
    client = _organizer_client("org@example.com")
    payload = {
        "email": "gate@example.com",
        "name": "G",
        "password": PASSWORD,
        "role": "RECEPTIONIST",
    }

    response = client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == HTTPStatus.CREATED
    assert User.objects.filter(role=User.Role.RECEPTIONIST).exists()


@pytest.mark.django_db
def test_customer_cannot_register_receptionist() -> None:
    customer = User.objects.create_user(
        email="cust@example.com",
        password=PASSWORD,
    )
    client = _client_with_access_token(customer)
    payload = {
        "email": "gate@example.com",
        "name": "G",
        "password": PASSWORD,
        "role": "RECEPTIONIST",
    }

    response = client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == HTTPStatus.FORBIDDEN


LOGIN_URL = "/api/auth/login/"
REFRESH_URL = "/api/auth/refresh/"
LOGOUT_URL = "/api/auth/logout/"
ME_URL = "/api/auth/me/"


@pytest.mark.django_db
def test_login_returns_user_and_sets_cookies() -> None:
    User.objects.create_user(
        email="login@example.com",
        password=PASSWORD,
        name="Logan",
    )
    client = APIClient()

    response = client.post(
        LOGIN_URL,
        {"email": "login@example.com", "password": PASSWORD},
        format="json",
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["user"]["email"] == "login@example.com"
    assert response.cookies["access_token"]["httponly"]
    assert response.cookies["refresh_token"]["httponly"]

    assert "access" not in response.json()
    assert "refresh" not in response.json()


@pytest.mark.django_db
def test_login_with_wrong_password_returns_401_and_no_cookies() -> None:
    User.objects.create_user(
        email="login@example.com",
        password=PASSWORD,
    )
    client = APIClient()

    response = client.post(
        LOGIN_URL,
        {"email": "login@example.com", "password": "wrong-password"},
        format="json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert not response.cookies


@pytest.mark.django_db
def test_me_requires_access_cookie() -> None:
    client = APIClient()

    response = client.get(ME_URL)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_me_returns_current_user_from_access_cookie() -> None:
    client = _organizer_client("me@example.com")

    response = client.get(ME_URL)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == "me@example.com"
    assert response.json()["role"] == "ORGANIZER"


@pytest.mark.django_db
def test_me_patch_updates_only_name() -> None:
    client = _organizer_client("patch@example.com")

    response = client.patch(
        ME_URL,
        {
            "name": "New Name",
            "email": "hacked@example.com",
            "role": "CUSTOMER",
        },
        format="json",
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "New Name"
    user = User.objects.get(email="patch@example.com")
    assert user.name == "New Name"
    assert user.role == User.Role.ORGANIZER


def _login(email: str) -> tuple[APIClient, str, str]:
    client = APIClient()
    response = client.post(
        LOGIN_URL,
        {"email": email, "password": PASSWORD},
        format="json",
    )
    access = response.cookies["access_token"].value
    refresh = response.cookies["refresh_token"].value
    return client, access, refresh


@pytest.mark.django_db
def test_refresh_rotates_cookies() -> None:
    User.objects.create_user(
        email="refresh@example.com",
        password=PASSWORD,
    )
    _, _, old_refresh = _login("refresh@example.com")
    client = APIClient()
    client.cookies["refresh_token"] = old_refresh

    response = client.post(REFRESH_URL)

    assert response.status_code == HTTPStatus.OK
    new_access = response.cookies["access_token"].value
    new_refresh = response.cookies["refresh_token"].value
    assert new_access
    assert new_refresh != old_refresh

    replay = APIClient()
    replay.cookies["refresh_token"] = old_refresh
    assert replay.post(REFRESH_URL).status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_refresh_without_cookie_returns_401() -> None:
    client = APIClient()

    response = client.post(REFRESH_URL)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_logout_clears_cookies_and_blacklists_refresh() -> None:
    User.objects.create_user(
        email="bye@example.com",
        password=PASSWORD,
    )
    client, _, refresh = _login("bye@example.com")

    response = client.post(LOGOUT_URL)

    assert response.status_code == HTTPStatus.OK
    assert response.cookies["access_token"].value == ""
    assert response.cookies["refresh_token"].value == ""

    fresh = APIClient()
    fresh.cookies["refresh_token"] = refresh
    assert fresh.post(REFRESH_URL).status_code == HTTPStatus.UNAUTHORIZED
