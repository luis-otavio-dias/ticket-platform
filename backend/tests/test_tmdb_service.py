"""Tests for TMDbCatalogService — all HTTP calls are mocked."""

import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from event.services import TMDbAPIError, TMDbCatalogService

SEARCH_RESPONSE = {
    "page": 1,
    "results": [
        {"id": 550, "title": "Fight Club", "poster_path": "/poster.jpg"}
    ],
    "total_pages": 1,
    "total_results": 1,
}

MOVIE_DETAIL = {
    "id": 550,
    "title": "Fight Club",
    "overview": "An insomniac office worker...",
    "runtime": 139,
}

DISCOVER_RESPONSE = {
    "page": 1,
    "results": [{"id": 27205, "title": "Inception"}],
    "total_pages": 500,
    "total_results": 10000,
}


def _make_mock_response(data: dict, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.read.return_value = json.dumps(data).encode()
    mock.status = status
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


@patch("event.services.urllib.request.urlopen")
def test_search_movies_calls_correct_url(mock_urlopen):
    mock_urlopen.return_value = _make_mock_response(SEARCH_RESPONSE)
    service = TMDbCatalogService()

    result = service.search_movies("Fight Club", page=1)

    assert result == SEARCH_RESPONSE
    call_args = mock_urlopen.call_args
    request_obj = call_args[0][0]
    assert "search/movie" in request_obj.full_url
    assert (
        "Fight+Club" in request_obj.full_url
        or "Fight%20Club" in request_obj.full_url
    )


@patch("event.services.urllib.request.urlopen")
def test_get_movie_calls_correct_url(mock_urlopen):
    mock_urlopen.return_value = _make_mock_response(MOVIE_DETAIL)
    service = TMDbCatalogService()

    result = service.get_movie(550)

    assert result == MOVIE_DETAIL
    call_args = mock_urlopen.call_args
    request_obj = call_args[0][0]
    assert "/movie/550" in request_obj.full_url


@patch("event.services.urllib.request.urlopen")
def test_discover_movies_calls_correct_url(mock_urlopen):
    mock_urlopen.return_value = _make_mock_response(DISCOVER_RESPONSE)
    service = TMDbCatalogService()

    result = service.discover_movies(page=2)

    assert result == DISCOVER_RESPONSE
    call_args = mock_urlopen.call_args
    request_obj = call_args[0][0]
    assert "discover/movie" in request_obj.full_url
    assert "page=2" in request_obj.full_url


@patch("event.services.urllib.request.urlopen")
def test_search_sends_bearer_token(mock_urlopen):
    mock_urlopen.return_value = _make_mock_response(SEARCH_RESPONSE)
    service = TMDbCatalogService()
    service._token = "test-token-abc"

    service.search_movies("inception")

    request_obj = mock_urlopen.call_args[0][0]
    assert request_obj.get_header("Authorization") == "Bearer test-token-abc"


@patch("event.services.urllib.request.urlopen")
def test_tmdb_http_error_raises_tmdb_api_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="https://api.themoviedb.org/3/search/movie",
        code=401,
        msg="Unauthorized",
        hdrs=None,  # type: ignore[arg-type]
        fp=None,
    )
    service = TMDbCatalogService()

    with pytest.raises(TMDbAPIError, match="401"):
        service.search_movies("inception")
