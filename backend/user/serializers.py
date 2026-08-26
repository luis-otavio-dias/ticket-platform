"""Serializers for the user app."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import exceptions, serializers

from user.models import User as UserModel


class UserSerializer(serializers.ModelSerializer[UserModel]):
    class Meta:
        model = UserModel
        fields = ["id", "email", "name", "role"]  # noqa: RUF012
        read_only_fields = ["id", "email", "role"]  # noqa: RUF012


class RegisterSerializer(serializers.ModelSerializer[UserModel]):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ["id", "email", "name", "password", "role"]  # noqa: RUF012
        read_only_fields = ["id"]  # noqa: RUF012

    def validate_password(self, value: str) -> str:
        candidate = get_user_model()(
            email=self.initial_data.get("email", ""),
            name=self.initial_data.get("name", ""),
        )
        validate_password(value, user=candidate)
        return value

    def validate_role(self, value: str) -> str:
        if value != UserModel.Role.RECEPTIONIST:
            return value

        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated or not user.is_organizer:
            msg = "Only authenticated organizers can register a receptionist."
            raise exceptions.PermissionDenied(msg)
        return value

    def create(self, validated_data: dict) -> UserModel:
        return UserModel.objects.create_user(**validated_data)
