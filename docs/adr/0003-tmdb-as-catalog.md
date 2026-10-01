# TMDb as the external event catalog

The platform requires an external catalog from which organizers select items to
create events. We chose The Movie Database (TMDb) API v3 as the catalog source.

## Decision

Use TMDb API v3 as the external catalog. Organizers search for movies in TMDb
and create events from them. The `tmdb_movie_id` field in `Event` stores the
TMDb movie ID for reference.

## Rationale

- Free tier with generous rate limits (40 req/10s)
- Rich metadata: title, overview, poster, genres, ratings, release date
- Well-documented REST API with Bearer token auth (Read Access Token)
- Portuguese language support via `language=pt-BR`
- No per-user auth required — a single system-level token is enough

## Integration Pattern

`TMDbCatalogService` wraps stdlib `urllib.request` calls. The backend acts
as a proxy — the frontend never calls TMDb directly. This prevents token
leakage and allows server-side caching in the future.

The token is stored as `TMDB_API_TOKEN` in the `.env` file and read via
`settings.TMDB_API_TOKEN`. It is a **system-level** credential (one per
deployment), not per-user.

## TMDb Endpoints Used

| Our endpoint | TMDb endpoint |
|---|---|
| `GET /api/events/catalog/search/?query=...` | `GET /search/movie` |
| `GET /api/events/catalog/discover/` | `GET /discover/movie` |
| `GET /api/events/catalog/<movie_id>/` | `GET /movie/{movie_id}` |

## Consequences

- Requires `TMDB_API_TOKEN` in the environment; without it the catalog
  endpoints return empty/error responses.
- If TMDb is unreachable, catalog endpoints return `502 Bad Gateway`
  via `TMDbAPIError`.
- Tests mock `urllib.request.urlopen` to avoid real network calls.
- `httpx` was not added as a dependency to keep the install footprint small;
  `urllib.request` (stdlib) is sufficient for synchronous Django views.
