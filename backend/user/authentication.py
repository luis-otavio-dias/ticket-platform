"""Cookie helpers for JWT auth via httpOnly cookies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

if TYPE_CHECKING:
    from django.http import HttpResponse
    from rest_framework.request import Request

ACCESS_COOKIE_DEFAULT = "access_token"
REFRESH_COOKIE_DEFAULT = "refresh_token"


def _jwt_settings() -> dict[str, Any]:
    return getattr(settings, "SIMPLE_JWT", {})


def _cookie_name(key: str, default: str) -> str:
    return str(_jwt_settings().get(key, default))


def get_refresh_token(request: Request) -> str | None:
    """Return the raw refresh token from its cookie, if present."""
    return request.COOKIES.get(
        _cookie_name("AUTH_COOKIE_REFRESH", REFRESH_COOKIE_DEFAULT)
    )


class CookieJWTAuthentication(JWTAuthentication):
    """
    JWT authentication that reads the access token from an httpOnly cookie
    instead of the Authorization header.
    """

    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        raw_token = request.COOKIES.get(
            _cookie_name("AUTH_COOKIE", ACCESS_COOKIE_DEFAULT)
        )
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token.encode())
        user = self.get_user(validated_token)
        return (user, validated_token)


def _cookie_options() -> dict[str, Any]:
    jwt_settings = _jwt_settings()
    return {
        "secure": bool(jwt_settings["AUTH_COOKIE_SECURE"]),
        "httponly": bool(jwt_settings["AUTH_COOKIE_HTTP_ONLY"]),
        "samesite": jwt_settings["AUTH_COOKIE_SAMESITE"],
        "path": jwt_settings.get("AUTH_COOKIE_PATH", "/"),
        "domain": jwt_settings.get("AUTH_COOKIE_DOMAIN"),
    }


def set_auth_cookies(
    response: HttpResponse,
    *,
    access_token: str,
    refresh_token: str | None,
) -> None:
    """Attach access and refresh tokens as httpOnly cookies."""
    options = _cookie_options()
    jwt_settings = _jwt_settings()

    response.set_cookie(
        key=_cookie_name("AUTH_COOKIE", ACCESS_COOKIE_DEFAULT),
        value=access_token,
        max_age=int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        **options,
    )
    if refresh_token is not None:
        response.set_cookie(
            key=_cookie_name("AUTH_COOKIE_REFRESH", REFRESH_COOKIE_DEFAULT),
            value=refresh_token,
            max_age=int(
                jwt_settings["REFRESH_TOKEN_LIFETIME"].total_seconds()
            ),
            **options,
        )


def clear_auth_cookies(response: HttpResponse) -> None:
    """Expire the auth cookies on the client."""
    options = _cookie_options()
    # delete_cookie() accepts a narrower set of kwargs than set_cookie().
    options.pop("secure", None)
    options.pop("httponly", None)
    response.delete_cookie(
        key=_cookie_name("AUTH_COOKIE", ACCESS_COOKIE_DEFAULT), **options
    )
    response.delete_cookie(
        key=_cookie_name("AUTH_COOKIE_REFRESH", REFRESH_COOKIE_DEFAULT),
        **options,
    )
