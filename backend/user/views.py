from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any, cast

from rest_framework import exceptions, status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.authentication import (
    clear_auth_cookies,
    get_refresh_token,
    set_auth_cookies,
)
from user.models import User
from user.serializers import RegisterSerializer, UserSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class RegisterView(CreateAPIView[User]):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # noqa: RUF012

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )
        set_auth_cookies(
            response,
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
        )
        return response


class LoginView(TokenObtainPairView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TokenObtainPairSerializer sets .user at runtime; not in stubs.
        user = cast("User", serializer.user)  # type: ignore[attr-defined]
        response = Response({"user": UserSerializer(user).data})
        set_auth_cookies(
            response,
            access_token=serializer.validated_data["access"],
            refresh_token=serializer.validated_data["refresh"],
        )
        return response


class RefreshView(TokenRefreshView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        raw_refresh = get_refresh_token(request)
        if raw_refresh is None:
            msg = "Refresh token cookie is missing."
            raise exceptions.AuthenticationFailed(msg)

        serializer = self.get_serializer(data={"refresh": raw_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise exceptions.AuthenticationFailed(exc.args[0]) from exc

        data = dict(serializer.validated_data)
        access = data.pop("access")
        refresh = data.pop("refresh", None)

        response = Response({"detail": "Token refreshed."})
        set_auth_cookies(
            response,
            access_token=str(access),
            refresh_token=str(refresh) if refresh else None,
        )
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]  # noqa: RUF012

    def post(self, request: Request) -> Response:
        raw_refresh = get_refresh_token(request)
        if raw_refresh:
            with suppress(TokenError):
                # Upstream annotates the token arg as Optional[Token].
                RefreshToken(raw_refresh).blacklist()  # type: ignore[arg-type]

        response = Response({"detail": "Logged out."})
        clear_auth_cookies(response)
        return response


class UserProfileView(RetrieveUpdateAPIView[User]):
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return cast("User", self.request.user)
