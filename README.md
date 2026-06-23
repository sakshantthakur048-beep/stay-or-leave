[README.md](https://github.com/user-attachments/files/29243118/README.md)
# Stay or Leave

Decide whether to stay or leave a country, city, company, or college — backed by side-by-side data and real user reviews.

## Stack

- **Frontend:** Plain HTML5 / CSS3 / JavaScript (no framework, no build step)
- **Backend:** Python 3 + Flask
- **Database:** PostgreSQL
- **Auth:** JWT (access + refresh tokens), bcrypt password hashing

## Project structure

```
stay-or-leave/
├── frontend/           # static site — open directly or serve with any web server
│   ├── *.html
│   ├── css/
│   └── js/
├── backend/
│   ├── app.py                 # Flask app factory + entry point
│   ├── config/config.py       # env-driven configuration
│   ├── extensions.py          # shared SQLAlchemy/JWT/etc instances
│   ├── models/                # SQLAlchemy models
│   ├── routes/                # Flask blueprints (thin HTTP layer)
│   ├── controllers/           # business logic
│   ├── middleware/             # auth guards, validation, error handlers
│   ├── database/
│   │   ├── schema.sql          # full Postgres schema
│   │   ├── seed.sql            # sample data
│   │   └── init_db.py          # alternative: create tables via SQLAlchemy
│   ├── uploads/                 # user-uploaded files (created at runtime)
│   └── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Database

Create a PostgreSQL database and user:

```sql
CREATE DATABASE stay_or_leave;
CREATE USER stayorleave_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE stay_or_leave TO stayorleave_user;
```

Load the schema and sample data:

```bash
psql -U stayorleave_user -d stay_or_leave -f backend/database/schema.sql
psql -U stayorleave_user -d stay_or_leave -f backend/database/seed.sql
```

(Alternatively, skip `schema.sql` and run `python backend/database/init_db.py` once your `.env` is set up — it creates tables from the SQLAlchemy models directly. You'd still want `seed.sql`'s data, adapted to skip the `uuid_generate_v4()` calls if you go this route, or just use `schema.sql`.)

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example ../.env
# edit ../.env with your real DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, etc.

python app.py
```

The API runs at `http://localhost:5000`. Health check: `GET /api/health`.

### 3. Frontend

The frontend is plain static files — no build step. Serve it with any static file server, e.g.:

```bash
cd frontend
python -m http.server 5500
```

Visit `http://localhost:5500`. Make sure `CORS_ORIGINS` in `.env` includes this origin (it does by default).

If you deploy the frontend on a different host/port than the API, set `window.STAY_OR_LEAVE_API_BASE` (in a `<script>` tag before `js/api.js` loads) to the full API URL.

## Sample accounts (from seed.sql)

| Role  | Email                  | Password       |
|-------|------------------------|----------------|
| Admin | admin@stayorleave.com  | Admin@12345    |
| User  | jordan@example.com     | *(seed hash is a placeholder — register a fresh account instead)* |

**Change the admin password immediately in any real deployment.**

## API overview

All endpoints are prefixed with `/api`.

| Area        | Endpoints |
|-------------|-----------|
| Auth        | `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/verify-email`, `GET /auth/me` |
| Users       | `PUT /users/me`, `POST /users/me/avatar`, `GET /users/<id>` |
| Places      | `GET /places`, `GET /places/<slug>` |
| Comparisons | `GET /comparisons/compare?place_a=&place_b=`, `POST /comparisons`, `GET /comparisons/featured`, `GET /comparisons/<id>`, `POST /comparisons/<id>/bookmark`, `GET /comparisons/bookmarks`, `GET /comparisons/export-pdf` |
| Reviews     | `GET/POST /reviews`, `PUT/DELETE /reviews/<id>`, `POST /reviews/<id>/images`, `POST /reviews/<id>/like`, `GET/POST /reviews/<id>/comments`, `POST /reviews/<id>/report` |
| Contact     | `POST /contact` |
| Admin       | `GET /admin/stats`, `/admin/users`, `/admin/reviews`, `/admin/reports`, `/admin/messages`, plus moderation actions (all require an admin JWT) |

## Notes on the "AI-generated summary"

The comparison page's narrative summary is produced by a deterministic, rule-based generator (`backend/controllers/comparison_controller.py::generate_ai_summary`) that reads the actual metric deltas between two places and writes sentences from them — no external LLM API key required. The function is isolated so it can be swapped for a real LLM call later without touching any other code.

## Security measures implemented

- Passwords hashed with bcrypt
- JWT access + refresh tokens
- Per-route rate limiting (Flask-Limiter)
- Input validation and sanitization on all write endpoints
- Role-based access control (`admin_required` decorator) for admin routes
- File upload type/size restrictions
- Parameterized queries throughout (SQLAlchemy ORM — no raw SQL string interpolation)
- CORS restricted to configured origins
- Generic error responses that don't leak internals

## What's intentionally out of scope for this build

Per the agreed core-scope decision, this build focuses on a fully working core flow: auth, place comparisons with charts/PDF export, and reviews/comments/likes/reports, plus a working admin API. Not built: multi-language support, a dedicated analytics dashboard UI, search-history/trending widgets, and the admin dashboard frontend (the admin API routes exist and are ready for a UI to be layered on top).
