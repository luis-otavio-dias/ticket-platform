"""API tests for the event app endpoints."""

from datetime import timedelta
from http import HTTPStatus

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from event.models import Event, EventStaff
from user.models import User

PASSWORD = "S3cure-Passw0rd!"



def _make_user(email: str, role: str = User.Role.CUSTOMER) -> User:
    return User.objects.create_user(email=email, password=PASSWORD, role=role)


def _client_for(user: User) -> APIClient:
    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.cookies["access_token"] = str(refresh.access_token)
    return client


def _organizer_client(
    email: str = "org@example.com",
) -> tuple[User, APIClient]:
    user = _make_user(email, role=User.Role.ORGANIZER)
    return user, _client_for(user)


def _receptionist_client(
    email: str = "rec@example.com",
) -> tuple[User, APIClient]:
    user = _make_user(email, role=User.Role.RECEPTIONIST)
    return user, _client_for(user)


def _customer_client(
    email: str = "cust@example.com",
) -> tuple[User, APIClient]:
    user = _make_user(email, role=User.Role.CUSTOMER)
    return user, _client_for(user)


def _make_event(
    organizer: User,
    status: str = Event.Status.DRAFT,
    **kwargs,
) -> Event:
    now = timezone.now()
    defaults = {
        "title": "Test Event",
        "start_date": now + timedelta(days=1),
        "end_date": now + timedelta(days=2),
        "location": "Cinema A",
        "capacity": 100,
        "price": "25.00",
        "tmdb_movie_id": 550,
        "status": status,
        "organizer": organizer,
    }
    defaults.update(kwargs)
    return Event.objects.create(**defaults)


def _event_payload(**kwargs) -> dict:
    now = timezone.now()
    defaults = {
        "title": "Inception Night",
        "start_date": (now + timedelta(days=1)).isoformat(),
        "end_date": (now + timedelta(days=2)).isoformat(),
        "location": "Cinema X",
        "capacity": 200,
        "price": "45.00",
        "tmdb_movie_id": 27205,
        "poster_path": "/poster.jpg",
    }
    defaults.update(kwargs)
    return defaults


EVENTS_URL = "/api/events/"



@pytest.mark.django_db
def test_organizer_creates_event():
    org, client = _organizer_client()
    payload = _event_payload()

    response = client.post(EVENTS_URL, payload, format="json")

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["title"] == "Inception Night"
    assert data["status"] == "DRAFT"
    assert data["organizer"]["email"] == org.email


@pytest.mark.django_db
def test_customer_cannot_create_event():
    _, client = _customer_client()

    response = client.post(EVENTS_URL, _event_payload(), format="json")

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_anonymous_cannot_create_event():
    client = APIClient()

    response = client.post(EVENTS_URL, _event_payload(), format="json")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_start_after_end_returns_400():
    _, client = _organizer_client()
    now = timezone.now()
    payload = _event_payload(
        start_date=(now + timedelta(days=3)).isoformat(),
        end_date=(now + timedelta(days=1)).isoformat(),
    )

    response = client.post(EVENTS_URL, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_equal_start_end_returns_400():
    _, client = _organizer_client()
    same = (timezone.now() + timedelta(days=1)).isoformat()
    payload = _event_payload(start_date=same, end_date=same)

    response = client.post(EVENTS_URL, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST




@pytest.mark.django_db
def test_list_events_returns_only_published():
    org = _make_user("org@example.com", User.Role.ORGANIZER)
    _make_event(org, status=Event.Status.DRAFT)
    _make_event(org, status=Event.Status.PUBLISHED)
    _make_event(org, status=Event.Status.CANCELLED)

    client = APIClient()
    response = client.get(EVENTS_URL)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "PUBLISHED"


@pytest.mark.django_db
def test_list_events_is_public():
    org = _make_user("org@example.com", User.Role.ORGANIZER)
    _make_event(org, status=Event.Status.PUBLISHED)

    client = APIClient()
    response = client.get(EVENTS_URL)

    assert response.status_code == HTTPStatus.OK




@pytest.mark.django_db
def test_public_event_detail_is_accessible():
    org = _make_user("org@example.com", User.Role.ORGANIZER)
    event = _make_event(org, status=Event.Status.PUBLISHED)

    client = APIClient()
    response = client.get(f"{EVENTS_URL}{event.pk}/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == event.title


@pytest.mark.django_db
def test_draft_event_hidden_from_public():
    org = _make_user("org@example.com", User.Role.ORGANIZER)
    event = _make_event(org, status=Event.Status.DRAFT)

    client = APIClient()
    response = client.get(f"{EVENTS_URL}{event.pk}/")

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_organizer_sees_own_draft():
    org, client = _organizer_client()
    event = _make_event(org, status=Event.Status.DRAFT)

    response = client.get(f"{EVENTS_URL}{event.pk}/")

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_organizer_cannot_see_other_organizer_draft():
    org1 = _make_user("org1@example.com", User.Role.ORGANIZER)
    _, client2 = _organizer_client("org2@example.com")
    event = _make_event(org1, status=Event.Status.DRAFT)

    response = client2.get(f"{EVENTS_URL}{event.pk}/")

    assert response.status_code == HTTPStatus.NOT_FOUND




@pytest.mark.django_db
def test_organizer_updates_own_draft():
    org, client = _organizer_client()
    event = _make_event(org)

    response = client.patch(
        f"{EVENTS_URL}{event.pk}/",
        {"title": "New Title"},
        format="json",
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == "New Title"


@pytest.mark.django_db
def test_organizer_cannot_update_published_event():
    org, client = _organizer_client()
    event = _make_event(org, status=Event.Status.PUBLISHED)

    response = client.patch(
        f"{EVENTS_URL}{event.pk}/",
        {"title": "Hacked"},
        format="json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_organizer_cannot_update_other_organizer_event():
    org1 = _make_user("org1@example.com", User.Role.ORGANIZER)
    _, client2 = _organizer_client("org2@example.com")
    event = _make_event(org1)

    response = client2.patch(
        f"{EVENTS_URL}{event.pk}/",
        {"title": "Hacked"},
        format="json",
    )

    assert response.status_code == HTTPStatus.NOT_FOUND




@pytest.mark.django_db
def test_publish_draft_event():
    org, client = _organizer_client()
    event = _make_event(org)

    response = client.post(f"{EVENTS_URL}{event.pk}/publish/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "PUBLISHED"
    event.refresh_from_db()
    assert event.is_published


@pytest.mark.django_db
def test_publish_already_published_event_returns_400():
    org, client = _organizer_client()
    event = _make_event(org, status=Event.Status.PUBLISHED)

    response = client.post(f"{EVENTS_URL}{event.pk}/publish/")

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_cancel_draft_event():
    org, client = _organizer_client()
    event = _make_event(org)

    response = client.post(f"{EVENTS_URL}{event.pk}/cancel/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "CANCELLED"


@pytest.mark.django_db
def test_cancel_already_cancelled_returns_400():
    org, client = _organizer_client()
    event = _make_event(org, status=Event.Status.CANCELLED)

    response = client.post(f"{EVENTS_URL}{event.pk}/cancel/")

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_customer_cannot_publish_event():
    org = _make_user("org@example.com", User.Role.ORGANIZER)
    _, cust_client = _customer_client()
    event = _make_event(org)

    response = cust_client.post(f"{EVENTS_URL}{event.pk}/publish/")

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_add_receptionist_as_staff():
    org, client = _organizer_client()
    rec, _ = _receptionist_client()
    event = _make_event(org)

    response = client.post(
        f"{EVENTS_URL}{event.pk}/staff/",
        {"user_id": rec.pk},
        format="json",
    )

    assert response.status_code == HTTPStatus.CREATED
    assert EventStaff.objects.filter(event=event, user=rec).exists()


@pytest.mark.django_db
def test_add_non_receptionist_returns_400():
    org, client = _organizer_client()
    cust = _make_user("cust@example.com", User.Role.CUSTOMER)
    event = _make_event(org)

    response = client.post(
        f"{EVENTS_URL}{event.pk}/staff/",
        {"user_id": cust.pk},
        format="json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_add_duplicate_staff_returns_400():
    org, client = _organizer_client()
    rec, _ = _receptionist_client()
    event = _make_event(org)
    EventStaff.objects.create(event=event, user=rec)

    response = client.post(
        f"{EVENTS_URL}{event.pk}/staff/",
        {"user_id": rec.pk},
        format="json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_remove_staff():
    org, client = _organizer_client()
    rec, _ = _receptionist_client()
    event = _make_event(org)
    EventStaff.objects.create(event=event, user=rec)

    response = client.delete(f"{EVENTS_URL}{event.pk}/staff/{rec.pk}/")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not EventStaff.objects.filter(event=event, user=rec).exists()


@pytest.mark.django_db
def test_customer_cannot_add_staff():
    org = _make_user("org@example.com", User.Role.ORGANIZER)
    _, cust_client = _customer_client()
    rec = _make_user("rec@example.com", User.Role.RECEPTIONIST)
    event = _make_event(org)

    response = cust_client.post(
        f"{EVENTS_URL}{event.pk}/staff/",
        {"user_id": rec.pk},
        format="json",
    )

    assert response.status_code == HTTPStatus.FORBIDDEN



@pytest.mark.django_db
def test_receptionist_my_events():
    org = _make_user("org@example.com", User.Role.ORGANIZER)
    rec, rec_client = _receptionist_client()
    event = _make_event(org, status=Event.Status.PUBLISHED)
    EventStaff.objects.create(event=event, user=rec)
    # a second published event NOT linked
    _make_event(org, status=Event.Status.PUBLISHED, title="Other Event")

    response = rec_client.get("/api/events/my-events/")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == event.title


@pytest.mark.django_db
def test_organizer_my_organized():
    org, org_client = _organizer_client()
    org2 = _make_user("org2@example.com", User.Role.ORGANIZER)
    _make_event(org)
    _make_event(org)
    _make_event(org2)

    response = org_client.get("/api/events/my-organized/")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 2


@pytest.mark.django_db
def test_customer_cannot_access_my_events():
    _, cust_client = _customer_client()

    response = cust_client.get("/api/events/my-events/")

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_customer_cannot_access_my_organized():
    _, cust_client = _customer_client()

    response = cust_client.get("/api/events/my-organized/")

    assert response.status_code == HTTPStatus.FORBIDDEN
