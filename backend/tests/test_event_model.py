"""Tests for Event and EventStaff models."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from event.models import Event, EventStaff
from user.models import User

PASSWORD = "S3cure-Passw0rd!"


def make_organizer(email: str = "org@example.com") -> User:
    return User.objects.create_user(
        email=email, password=PASSWORD, role=User.Role.ORGANIZER
    )


def make_receptionist(email: str = "rec@example.com") -> User:
    return User.objects.create_user(
        email=email, password=PASSWORD, role=User.Role.RECEPTIONIST
    )


def make_event(organizer: User, **kwargs) -> Event:
    now = timezone.now()
    defaults = {
        "title": "Test Event",
        "start_date": now + timedelta(days=1),
        "end_date": now + timedelta(days=2),
        "location": "Cinema A",
        "capacity": 100,
        "price": "25.00",
        "tmdb_movie_id": 550,
        "organizer": organizer,
    }
    defaults.update(kwargs)
    return Event.objects.create(**defaults)


@pytest.mark.django_db
class TestEventModel:
    def test_create_event_with_valid_data(self):
        org = make_organizer()
        event = make_event(org)

        assert event.pk is not None
        assert event.title == "Test Event"
        assert event.capacity == 100
        assert event.tmdb_movie_id == 550

    def test_default_status_is_draft(self):
        org = make_organizer()
        event = make_event(org)

        assert event.status == Event.Status.DRAFT

    def test_str_returns_title(self):
        org = make_organizer()
        event = make_event(org, title="Inception Night")

        assert str(event) == "Inception Night"

    def test_is_draft_property(self):
        org = make_organizer()
        event = make_event(org)

        assert event.is_draft
        assert not event.is_published
        assert not event.is_cancelled

    def test_is_published_property(self):
        org = make_organizer()
        event = make_event(org, status=Event.Status.PUBLISHED)

        assert event.is_published
        assert not event.is_draft
        assert not event.is_cancelled

    def test_is_cancelled_property(self):
        org = make_organizer()
        event = make_event(org, status=Event.Status.CANCELLED)

        assert event.is_cancelled
        assert not event.is_draft
        assert not event.is_published

    def test_event_ordering_most_recent_first(self):
        org = make_organizer()
        now = timezone.now()
        e1 = make_event(
            org,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
        )
        e2 = make_event(
            org,
            start_date=now + timedelta(days=5),
            end_date=now + timedelta(days=6),
        )

        events = list(Event.objects.all())

        assert events[0].pk == e2.pk
        assert events[1].pk == e1.pk

    def test_event_auto_timestamps(self):
        org = make_organizer()
        event = make_event(org)

        assert event.created_at is not None
        assert event.updated_at is not None


@pytest.mark.django_db
class TestEventStaffModel:
    def test_create_event_staff(self):
        org = make_organizer()
        rec = make_receptionist()
        event = make_event(org)

        staff = EventStaff.objects.create(event=event, user=rec)

        assert staff.pk is not None

    def test_event_staff_str(self):
        org = make_organizer()
        rec = make_receptionist("gate@example.com")
        event = make_event(org, title="Fight Club Screening")

        staff = EventStaff.objects.create(event=event, user=rec)

        assert str(staff) == "gate@example.com @ Fight Club Screening"

    def test_event_staff_unique_together(self):
        org = make_organizer()
        rec = make_receptionist()
        event = make_event(org)
        EventStaff.objects.create(event=event, user=rec)

        with pytest.raises(IntegrityError):
            EventStaff.objects.create(event=event, user=rec)
