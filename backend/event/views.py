from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from event.models import Event, EventStaff
from event.permissions import IsOrganizer, IsReceptionist
from event.serializers import (
    EventCreateSerializer,
    EventDetailSerializer,
    EventListSerializer,
    EventStaffSerializer,
    EventUpdateSerializer,
)
from event.services import TMDbAPIError, TMDbCatalogService

if TYPE_CHECKING:
    from rest_framework.request import Request

    from user.models import User


class CatalogSearchView(APIView):
    """GET /api/events/catalog/search/?query=<title>&page=<n>

    Proxies the TMDb search/movie endpoint for organizers to browse the
    external catalog before creating an event.
    """

    permission_classes = [IsOrganizer]  # noqa: RUF012

    def get(self, request: Request) -> Response:
        query = request.query_params.get("query", "")
        page = int(request.query_params.get("page", 1))
        language = request.query_params.get("language", "pt-BR")

        service = TMDbCatalogService()
        try:
            data = service.search_movies(query, page=page, language=language)
        except TMDbAPIError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)


class CatalogDiscoverView(APIView):
    """GET /api/events/catalog/discover/?page=<n>

    Proxies the TMDb discover/movie endpoint (popular movies).
    """

    permission_classes = [IsOrganizer]  # noqa: RUF012

    def get(self, request: Request) -> Response:
        page = int(request.query_params.get("page", 1))
        language = request.query_params.get("language", "pt-BR")
        sort_by = request.query_params.get("sort_by", "popularity.desc")

        service = TMDbCatalogService()
        try:
            data = service.discover_movies(
                page=page, language=language, sort_by=sort_by
            )
        except TMDbAPIError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)


class CatalogMovieDetailView(APIView):
    """GET /api/events/catalog/<movie_id>/

    Proxies the TMDb movie/{id} endpoint for a single movie's details.
    """

    permission_classes = [IsOrganizer]  # noqa: RUF012

    def get(self, request: Request, movie_id: int) -> Response:
        language = request.query_params.get("language", "pt-BR")
        service = TMDbCatalogService()
        try:
            data = service.get_movie(movie_id, language=language)
        except TMDbAPIError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)




class EventListCreateView(APIView):
    """GET /api/events/ — public list of PUBLISHED events.
    POST /api/events/ — organizer creates a new DRAFT event.
    """

    def get_permissions(self) -> list[Any]:
        if self.request.method == "POST":
            return [IsOrganizer()]
        return [AllowAny()]

    def get(self, request: Request) -> Response:
        events = Event.objects.filter(
            status=Event.Status.PUBLISHED
        ).select_related("organizer")
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = EventCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        return Response(
            EventDetailSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )




class EventDetailUpdateView(APIView):
    """GET /api/events/<pk>/ — public for PUBLISHED, organizer for own DRAFT.
    PATCH /api/events/<pk>/ — organizer partially updates own DRAFT event.
    """

    def get_permissions(self) -> list[Any]:
        if self.request.method == "PATCH":
            return [IsOrganizer()]
        return [AllowAny()]

    def _get_event(self, request: Request, pk: int) -> Event | None:
        try:
            event = (
                Event.objects.select_related("organizer")
                .prefetch_related("staff__user")
                .get(pk=pk)
            )
        except Event.DoesNotExist:
            return None
        return event

    def get(self, request: Request, pk: int) -> Response:
        event = self._get_event(request, pk)
        if event is None:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )


        if not event.is_published:
            if not request.user.is_authenticated or (
                not request.user.is_organizer
            ):
                return Response(
                    {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if event.organizer_id != request.user.pk:
                return Response(
                    {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(EventDetailSerializer(event).data)

    def patch(self, request: Request, pk: int) -> Response:
        if not request.user.is_authenticated or not request.user.is_organizer:
            return Response(
                {"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN
            )

        user = cast("User", request.user)
        try:
            event = Event.objects.get(pk=pk, organizer=user)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not event.is_draft:
            return Response(
                {"detail": "Only DRAFT events can be updated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EventUpdateSerializer(
            event, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        event.refresh_from_db()
        return Response(EventDetailSerializer(event).data)



class EventPublishView(APIView):
    """POST /api/events/<pk>/publish/ — organizer publishes own DRAFT event."""

    permission_classes = [IsOrganizer]  # noqa: RUF012

    def post(self, request: Request, pk: int) -> Response:
        user = cast("User", request.user)
        try:
            event = Event.objects.get(pk=pk, organizer=user)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not event.is_draft:
            return Response(
                {"detail": "Only DRAFT events can be published."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.status = Event.Status.PUBLISHED
        event.save(update_fields=["status", "updated_at"])
        return Response(EventDetailSerializer(event).data)


class EventCancelView(APIView):
    """POST /api/events/<pk>/cancel/ — organizer cancels own event."""

    permission_classes = [IsOrganizer]  # noqa: RUF012

    def post(self, request: Request, pk: int) -> Response:
        user = cast("User", request.user)
        try:
            event = Event.objects.get(pk=pk, organizer=user)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if event.is_cancelled:
            return Response(
                {"detail": "Event is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.status = Event.Status.CANCELLED
        event.save(update_fields=["status", "updated_at"])
        return Response(EventDetailSerializer(event).data)




class EventStaffView(APIView):
    """POST /api/events/<pk>/staff/ — organizer adds a RECEPTIONIST.
    DELETE /api/events/<pk>/staff/<user_id>/ — organizer removes staff.
    """

    permission_classes = [IsOrganizer]  # noqa: RUF012

    def _get_own_event(self, request: Request, pk: int) -> Event | Response:
        user = cast("User", request.user)
        try:
            return Event.objects.get(pk=pk, organizer=user)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request: Request, pk: int) -> Response:
        result = self._get_own_event(request, pk)
        if isinstance(result, Response):
            return result
        event = result

        serializer = EventStaffSerializer(
            data=request.data, context={"event": event, "request": request}
        )
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        return Response(
            EventStaffSerializer(staff).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request: Request, pk: int, user_id: int) -> Response:
        result = self._get_own_event(request, pk)
        if isinstance(result, Response):
            return result
        event = result

        try:
            staff = EventStaff.objects.get(event=event, user_id=user_id)
        except EventStaff.DoesNotExist:
            return Response(
                {"detail": "Staff member not found for this event."},
                status=status.HTTP_404_NOT_FOUND,
            )

        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class MyEventsView(APIView):
    """GET /api/events/my-events/

    List events where the logged-in RECEPTIONIST is staff.
    """

    permission_classes = [IsReceptionist]  # noqa: RUF012

    def get(self, request: Request) -> Response:
        user = cast("User", request.user)
        event_ids = EventStaff.objects.filter(user=user).values_list(
            "event_id", flat=True
        )
        events = Event.objects.filter(
            pk__in=event_ids, status=Event.Status.PUBLISHED
        ).select_related("organizer")
        return Response(EventListSerializer(events, many=True).data)


class OrganizerEventsView(APIView):
    """GET /api/events/my-organized/

    List all events created by the logged-in ORGANIZER.
    """

    permission_classes = [IsOrganizer]  # noqa: RUF012

    def get(self, request: Request) -> Response:
        user = cast("User", request.user)
        events = Event.objects.filter(organizer=user).select_related(
            "organizer"
        )
        return Response(EventListSerializer(events, many=True).data)
