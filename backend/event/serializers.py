"""Serializers for the event app."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from event.models import Event, EventStaff
from user.models import User
from user.serializers import UserSerializer

if TYPE_CHECKING:
    from decimal import Decimal


class EventListSerializer(serializers.ModelSerializer[Event]):
    """Read-only serializer for event listings."""

    organizer = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [  # noqa: RUF012
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
            "capacity",
            "price",
            "status",
            "tmdb_movie_id",
            "poster_path",
            "organizer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EventStaffInlineSerializer(serializers.ModelSerializer[EventStaff]):
    """Nested staff representation used inside EventDetailSerializer."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = EventStaff
        fields = ["id", "user"]  # noqa: RUF012
        read_only_fields = fields


class EventDetailSerializer(EventListSerializer):
    """Full event detail, including staff list."""

    staff = EventStaffInlineSerializer(many=True, read_only=True)

    class Meta(EventListSerializer.Meta):
        fields = [*EventListSerializer.Meta.fields, "staff"]  # type: ignore[misc] # noqa: RUF012
        read_only_fields = fields  # type: ignore[misc]


class EventCreateSerializer(serializers.ModelSerializer[Event]):
    """Used by organizers to create a new event (DRAFT)."""

    class Meta:
        model = Event
        fields = [  # noqa: RUF012
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
            "capacity",
            "price",
            "tmdb_movie_id",
            "poster_path",
        ]

    def validate_price(self, value: Decimal) -> Decimal:
        if value < 0:
            msg = "price must be non-negative."
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["start_date"] >= attrs["end_date"]:
            msg = "start_date must be before end_date."
            raise serializers.ValidationError(msg)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Event:
        request = self.context["request"]
        validated_data["organizer"] = request.user
        return super().create(validated_data)


class EventUpdateSerializer(serializers.ModelSerializer[Event]):
    """Used by organizers to partially update a DRAFT event."""

    class Meta:
        model = Event
        fields = [  # noqa: RUF012
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
            "capacity",
            "price",
        ]

    def validate_price(self, value: Decimal) -> Decimal:
        if value < 0:
            msg = "price must be non-negative."
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        instance = self.instance
        start = attrs.get("start_date", instance.start_date)  # type: ignore[union-attr]
        end = attrs.get("end_date", instance.end_date)  # type: ignore[union-attr]
        if start >= end:
            msg = "start_date must be before end_date."
            raise serializers.ValidationError(msg)
        return attrs


class EventStaffSerializer(serializers.ModelSerializer[EventStaff]):
    """Add a RECEPTIONIST user as staff to an event."""

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = EventStaff
        fields = ["id", "user", "user_id"]  # noqa: RUF012
        read_only_fields = ["id", "user"]  # noqa: RUF012

    def validate_user_id(self, value: int) -> int:
        try:
            user: User = User.objects.get(pk=value)
        except User.DoesNotExist:
            msg = "User not found."
            raise serializers.ValidationError(msg)  # noqa: B904
        if not user.is_receptionist:
            msg = "Only RECEPTIONIST users can be added as event staff."
            raise serializers.ValidationError(msg)
        return value

    def create(self, validated_data: dict[str, Any]) -> EventStaff:
        event: Event = self.context["event"]
        user: User = User.objects.get(pk=validated_data["user_id"])
        staff, created = EventStaff.objects.get_or_create(
            event=event, user=user
        )
        if not created:
            msg = "This user is already staff for this event."
            raise serializers.ValidationError(msg)
        return staff
