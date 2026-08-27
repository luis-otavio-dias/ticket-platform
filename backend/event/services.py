"""TMDb API v3 catalog service using stdlib urllib (no extra deps)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from django.conf import settings

TMDB_BASE_URL = "https://api.themoviedb.org/3"


class TMDbAPIError(Exception):
    """Raised when the TMDb API returns a non-2xx response."""


class TMDbCatalogService:
    """Proxy service for the TMDb API v3.

    Uses stdlib ``urllib`` so no extra dependencies are required.
    The Read Access Token is read from ``settings.TMDB_API_TOKEN``.
    """

    def __init__(self) -> None:
        self._token: str = getattr(settings, "TMDB_API_TOKEN", "")

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform a GET request to the TMDb API and return parsed JSON."""
        url = f"{TMDB_BASE_URL}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(  # noqa: S310
            url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:  # noqa: S310
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            msg = f"TMDb API error {exc.code}: {exc.reason}"
            raise TMDbAPIError(msg) from exc
        except urllib.error.URLError as exc:
            msg = f"TMDb API unreachable: {exc.reason}"
            raise TMDbAPIError(msg) from exc

    def search_movies(
        self,
        query: str,
        *,
        page: int = 1,
        language: str = "pt-BR",
    ) -> dict[str, Any]:
        """Search movies by title. Proxies GET /search/movie."""
        return self._get(
            "/search/movie",
            params={"query": query, "page": page, "language": language},
        )

    def get_movie(
        self,
        movie_id: int,
        *,
        language: str = "pt-BR",
    ) -> dict[str, Any]:
        """Get movie details by ID. Proxies GET /movie/{movie_id}."""
        return self._get(f"/movie/{movie_id}", params={"language": language})

    def discover_movies(
        self,
        *,
        page: int = 1,
        language: str = "pt-BR",
        sort_by: str = "popularity.desc",
    ) -> dict[str, Any]:
        """Discover popular movies. Proxies GET /discover/movie."""
        return self._get(
            "/discover/movie",
            params={"page": page, "language": language, "sort_by": sort_by},
        )
