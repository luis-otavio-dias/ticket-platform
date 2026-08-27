from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class IsOrganizer(BasePermission):
    """Only users with role ORGANIZER can access."""

    def has_permission(self, request: Request, view: APIView) -> bool:  # noqa: ARG002
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_organizer
        )


class IsReceptionist(BasePermission):
    """Only users with role RECEPTIONIST can access."""

    def has_permission(self, request: Request, view: APIView) -> bool:  # noqa: ARG002
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_receptionist
        )
