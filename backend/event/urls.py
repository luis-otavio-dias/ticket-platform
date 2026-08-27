from django.urls import path

from event import views

app_name = "event"

urlpatterns = [
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
    path("my-events/", views.MyEventsView.as_view(), name="my-events"),
    path(
        "my-organized/",
        views.OrganizerEventsView.as_view(),
        name="my-organized",
    ),
    path("", views.EventListCreateView.as_view(), name="list-create"),
    path(
        "<int:pk>/",
        views.EventDetailUpdateView.as_view(),
        name="detail-update",
    ),
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
