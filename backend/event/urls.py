from django.urls import path

from event import views

app_name = "event"

urlpatterns = [
    # ------------------------------------------------------------------
    # TMDb Catalog proxy (organizer only)
    # ------------------------------------------------------------------
    path(
        "catalog/search/",
        views.CatalogSearchView.as_view(),
        name="catalog-search",
    ),
    path(
        "catalog/discover/",
        views.CatalogDiscoverView.as_view(),
        name="catalog-discover",
    ),
    path(
        "catalog/<int:movie_id>/",
        views.CatalogMovieDetailView.as_view(),
        name="catalog-detail",
    ),
    # ------------------------------------------------------------------
    # Role-specific lists (must come before <pk> to avoid collision)
    # ------------------------------------------------------------------
    path("my-events/", views.MyEventsView.as_view(), name="my-events"),
    path(
        "my-organized/",
        views.OrganizerEventsView.as_view(),
        name="my-organized",
    ),
    # ------------------------------------------------------------------
    # Event CRUD
    # ------------------------------------------------------------------
    path("", views.EventListCreateView.as_view(), name="list-create"),
    path(
        "<int:pk>/",
        views.EventDetailUpdateView.as_view(),
        name="detail-update",
    ),
    # ------------------------------------------------------------------
    # Event lifecycle
    # ------------------------------------------------------------------
    path(
        "<int:pk>/publish/",
        views.EventPublishView.as_view(),
        name="publish",
    ),
    path(
        "<int:pk>/cancel/",
        views.EventCancelView.as_view(),
        name="cancel",
    ),
    # ------------------------------------------------------------------
    # Event staff
    # ------------------------------------------------------------------
    path(
        "<int:pk>/staff/",
        views.EventStaffView.as_view(),
        name="staff",
    ),
    path(
        "<int:pk>/staff/<int:user_id>/",
        views.EventStaffView.as_view(),
        name="staff-detail",
    ),
]
