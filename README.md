# Sentinel — connected frontend + backend

Scope of this pass: **auth only** — login, registration, and role-based
routing (admin vs member) go through the real FastAPI + PostgreSQL
backend. The admin dashboard's member list, activity log, and
surveillance events are stubbed (`Frontend/users_db.py`) and out of
scope for now — see the bottom of this file.

## 1. Backend

```bash
cd backend
pip install -r requirements.txt

cp .env.example .env
# edit .env: point PGHOST/PGPORT/PGUSER/PGPASSWORD (or DATABASE_URL)
# at your Postgres server

python init_db.py          # builds the identity schema — DESTRUCTIVE,
                            # drops the schema first if it exists
python create_admin.py     # provision at least one admin account;
                            # self-service registration only ever
                            # creates 'member' accounts

uvicorn main:app --host 0.0.0.0 --port 8000
```

`GET /health` reports `{"status": "ok", "database": "connected"}` once
the app server and Postgres are both reachable — check that first if
anything below isn't working.

## 2. Frontend

```bash
cd Frontend
pip install -r requirements.txt

cp .env.example .env
# edit .env: SENTINEL_API_URL should point at wherever uvicorn is
# running — http://127.0.0.1:8000 locally, or your server's real
# address/port once deployed

python main.py
```

## What changed from the original zip

- `Frontend/users_db.py` didn't exist in the upload (only its compiled
  `.pyc` was present). It's rebuilt here as an HTTP client with the
  same function names the GUI already calls, so `login.py` /
  `register.py` / `dashboard.py` / `admin_dashboard.py` needed no
  changes to their call sites.
- `backend/database.py` now reads the connection string from
  environment variables instead of a hardcoded, plaintext one.
- `backend/schema.sql` adds a `role` column (`admin`/`member`).
- `backend/main.py` adds `POST /login` (verifies the argon2 hash,
  generic error on bad username *or* password so it can't be used to
  enumerate accounts) and `GET /health`.
- `backend/create_admin.py` is new — the only way to create an admin
  account, since `/register` always creates members.
- `Frontend/register.py`'s client-side validation was quietly out of
  sync with what the backend actually accepts (it allowed `.`/`-` in
  usernames and passwords as short as 6 characters, backend rejects
  both) — tightened to match, so failures show up as a clear message
  in the form instead of a raw 422 after submitting.

## Not in this pass

`get_all_members`, `get_recent_activity`, `get_recent_events`,
`log_activity`, `add_event` are stubs returning empty results — the
admin dashboard will load but its live-data panels stay empty until
`activity_log` / `surveillance_events` tables and endpoints exist on
the backend.
