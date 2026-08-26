from __future__ import annotations

from typing import ClassVar, cast

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str,
        *,
        name: str = "",
        **extra_fields: str | bool,
    ) -> User:
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            msg = "Users must have an email address"
            raise ValueError(msg)

        email = self.normalize_email(email)
        user = cast("User", self.model(email=email, name=name, **extra_fields))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: str,
        *,
        name: str = "",
        **extra_fields: str | bool,
    ) -> User:
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, name=name, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str,
        *,
        name: str = "",
        **extra_fields: str | bool,
    ) -> User:
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)

        return self._create_user(email, password, name=name, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ORGANIZER = "ORGANIZER", "Organizador"
        RECEPTIONIST = "RECEPTIONIST", "Portaria"
        CUSTOMER = "CUSTOMER", "Cliente"

    email = models.EmailField(unique=True)
    username = None
    name = models.CharField(max_length=150, blank=True, default="")
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CUSTOMER
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects: CustomUserManager = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email

    @property
    def is_organizer(self) -> bool:
        return self.role == self.Role.ORGANIZER

    @property
    def is_customer(self) -> bool:
        return self.role == self.Role.CUSTOMER

    @property
    def is_receptionist(self) -> bool:
        return self.role == self.Role.RECEPTIONIST
