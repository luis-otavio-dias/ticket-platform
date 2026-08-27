from django.contrib import admin

from event.models import Event, EventStaff


class EventStaffInline(admin.TabularInline):
    model = EventStaff
    extra = 0
    raw_id_fields = ("user",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "organizer",
        "start_date",
        "end_date",
        "capacity",
        "price",
    )
    list_filter = ("status",)
    search_fields = ("title", "organizer__email")
    raw_id_fields = ("organizer",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [EventStaffInline]  # noqa: RUF012


@admin.register(EventStaff)
class EventStaffAdmin(admin.ModelAdmin):
    list_display = ("user", "event")
    search_fields = ("user__email", "event__title")
    raw_id_fields = ("user", "event")
