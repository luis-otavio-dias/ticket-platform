# JWT tokens delivered in httpOnly cookies

The API is consumed by a browser SPA (Vite + TypeScript). We decided to deliver
SimpleJWT access/refresh tokens as httpOnly cookies instead of returning them
in JSON bodies for the client to store and send via `Authorization: Bearer`.
This removes the XSS token-exfiltration vector since JavaScript can never read
the tokens; CORS is configured with `credentials` for the SPA origin.

Considered options:

- `Authorization` header + localStorage (simplejwt default) — rejected: any XSS
  reads the tokens.
- CSRF-token protected cookie sessions — rejected for this scope: we rely on
  `SameSite` + httpOnly instead, accepting cross-site POST risk on browsers that
  ignore SameSite.

Consequences:

- `SameSite=None` requires HTTPS, so production is `Secure+None` while dev is
  `Lax` over HTTP (`AUTH_COOKIE_*` settings are conditional on `DEBUG`).
- The frontend cannot log itself out (can't delete an httpOnly cookie), so a
  server logout endpoint is mandatory.
- Token refresh must also be cookie-driven: `/api/auth/refresh/` reads the
  refresh token from the cookie and re-sets rotated cookies.
