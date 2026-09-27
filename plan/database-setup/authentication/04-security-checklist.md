# Step 2.4 — Security Checklist

**Goal:** Document and implement minimum security practices before exposing the portal beyond local dev.

**Status:** ⬜ Not started  
**Depends on:** [02-auth-api.md](./02-auth-api.md), [03-frontend-auth.md](./03-frontend-auth.md)  
**Blocks:** Production deployment (recommended before public URL)

**Estimated effort:** 1 session (review + targeted fixes)

---

## Authentication

| Item | POC minimum | Production target |
|------|-------------|-------------------|
| JWT secret | Set `JWT_SECRET_KEY` in `.env` | Long random secret (32+ bytes), rotated on compromise |
| Token expiry | `JWT_EXPIRE_MINUTES=60` | Shorter access token + refresh token flow |
| Password storage | bcrypt via passlib | Same; consider argon2 later |
| Password rules | Min 8 characters | Min 8 + complexity or breach check (optional) |
| Rate limiting | Document only | `slowapi` or reverse proxy limit on `/auth/login` |
| Account enumeration | Generic "invalid credentials" on login | Same; avoid "email not found" vs "wrong password" |

---

## Transport

| Item | Action |
|------|--------|
| HTTPS | Required on any public server — use Caddy, Nginx + Let's Encrypt |
| HTTP → HTTPS redirect | Configure at reverse proxy |
| Secure cookies (if adopted) | `Secure`, `HttpOnly`, `SameSite=Lax` |

---

## CORS

**File:** `backend/app/config.py` — `cors_origins`

| Environment | Value |
|-------------|-------|
| Local dev | `http://localhost:5173` |
| Production | Exact frontend origin only — no `*` with credentials |

---

## Frontend token storage

| Risk | Mitigation |
|------|------------|
| XSS steals JWT from `localStorage` | Sanitize user content (DOMPurify already used); CSP headers; migrate to httpOnly cookies |
| Token in URL | Never pass token in query params |

---

## Database

Cross-reference [jobdb/04-production-hardening.md](../jobdb/04-production-hardening.md):

- [ ] Strong Postgres password
- [ ] Port 5432 not public
- [ ] Backups configured
- [ ] `.env` not committed

---

## API surface

| Item | Action |
|------|--------|
| OpenAPI `/docs` | Disable or protect in production (`DEBUG=false` flag) |
| Health endpoint | No secrets in response |
| Error messages | No stack traces to client in production |

---

## Dependencies

| Item | Action |
|------|--------|
| Python packages | `uv sync` with pinned versions in lockfile |
| npm packages | `npm audit` periodically |

---

## Implementation tasks (pick for POC deploy)

### Required before public deploy

1. Set strong `JWT_SECRET_KEY` and `POSTGRES_PASSWORD`
2. Enable HTTPS
3. Lock `CORS_ORIGINS` to production domain
4. Confirm Postgres not exposed publicly

### Recommended soon after

5. Add rate limiting on auth endpoints
6. Add `JWT_REFRESH` flow or shorter access token
7. Disable `/docs` in production
8. Add security headers via reverse proxy:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Content-Security-Policy` (tune for Vite assets)

### Future

9. Email verification on register
10. Password reset flow
11. OAuth (Google, GitHub)
12. Audit log for auth events

---

## Verification checklist

- [ ] `JWT_SECRET_KEY` is not default in production `.env`
- [ ] Login returns same error for wrong email vs wrong password
- [ ] CORS rejects requests from unknown origins
- [ ] HTTPS works end-to-end
- [ ] `/docs` inaccessible or auth-gated in production
- [ ] Security items documented in `docs/operations/deployment.md` or README

---

## Incident response (document only)

1. Rotate `JWT_SECRET_KEY` (invalidates all sessions)
2. Rotate Postgres password
3. Restore from backup if data compromised
4. Review access logs
