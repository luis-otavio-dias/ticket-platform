from __future__ import annotations

from django.conf import settings
from django.db import models


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PUBLISHED = "PUBLISHED", "Publicado"
        CANCELLED = "CANCELLED", "Cancelado"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    tmdb_movie_id = models.PositiveIntegerField(
        help_text="TMDb movie ID from the external catalog",
    )
    poster_path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="TMDb poster path, e.g. /kqjL17yufvn9OVLyXYpvtyrFfak.jpg",
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
        limit_choices_to={"role": "ORGANIZER"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "event"
        ordering = ["-start_date"]  # noqa: RUF012

    def __str__(self) -> str:
        return self.title

    @property
    def is_draft(self) -> bool:
        return self.status == self.Status.DRAFT

    @property
    def is_published(self) -> bool:
        return self.status == self.Status.PUBLISHED

    @property
    def is_cancelled(self) -> bool:
        return self.status == self.Status.CANCELLED


class EventStaff(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="staff",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_events",
        limit_choices_to={"role": "RECEPTIONIST"},
    )

    class Meta:
        db_table = "event_staff"
        unique_together = [("event", "user")]  # noqa: RUF012
        verbose_name = "Event Staff"
        verbose_name_plural = "Event Staff"

    def __str__(self) -> str:
        return f"{self.user.email} @ {self.event.title}"
