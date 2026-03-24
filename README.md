# AI Blog Studio

A full-stack blogging platform with an AI-powered writing assistant backed by **Anthropic Claude**.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.12), SQLAlchemy 2, Pydantic v2 |
| Database | PostgreSQL 16 |
| Cache / Rate Limiting | Redis 7 |
| AI | Anthropic Claude (`claude-3-5-sonnet`) |
| Auth | JWT (HS256, 15-min access tokens + httpOnly refresh cookie) |

## Project Structure

```
ai-blog-studio/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py          # App factory + /health
│   │   ├── config.py        # Pydantic settings
│   │   ├── database.py      # SQLAlchemy engine + Base
│   │   ├── modules/
│   │   │   ├── auth/          # Signup, login, JWT, /auth/me
│   │   │   ├── posts/         # CRUD + soft-delete + publish
│   │   │   └── ai/            # 5 Claude tools + Redis rate limiter
│   │   └── middleware/
│   │       └── sanitizer.py   # bleach HTML sanitiser
│   ├── alembic/             # DB migrations (5 versions)
│   └── tests/               # pytest suite (health, auth, posts, ai)
├── frontend/             # Next.js application
│   ├── app/
│   │   ├── (auth)/          # Login / Signup pages
│   │   ├── (blog)/          # SSR blog feed + single post (SEO meta)
│   │   └── (editor)/        # New post + edit post editors
│   ├── components/
│   │   ├── editor/          # MarkdownEditor, EditorSidebar, WordCount
│   │   ├── ai-tools/        # AIToolsPanel, AISuggestion
│   │   └── blog/            # BlogFeed, PostCard
│   └── lib/
│       ├── api.ts           # Typed API client
│       └── auth.ts          # JWT helpers
└── docker-compose.yml
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- An [Anthropic API key](https://console.anthropic.com)

### 1. Clone & configure
```bash
git clone https://github.com/arshtrehan2/ai-blog-studio.git
cd ai-blog-studio
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY and a strong JWT_SECRET_KEY
```

### 2. Start all services
```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Run backend tests locally
```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

## API Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/signup | — | Register |
| POST | /auth/login | — | Login |
| POST | /auth/logout | ✓ | Logout |
| GET | /auth/me | ✓ | Profile |
| POST | /posts | ✓ | Create post |
| GET | /posts | — | List published |
| GET | /posts/{id} | opt | Get post |
| PUT | /posts/{id} | ✓ | Update post |
| DELETE | /posts/{id} | ✓ | Soft-delete |
| PATCH | /posts/{id}/publish | ✓ | Publish draft |
| POST | /ai/improve | ✓ | Rewrite content |
| POST | /ai/summary | ✓ | Generate summary |
| POST | /ai/tags | ✓ | Suggest tags |
| POST | /ai/seo-title | ✓ | SEO title + meta |
| POST | /ai/tldr | ✓ | One-sentence TLDR |

> AI endpoints: **20 requests / user / hour** (Redis sliding window).

## Security Notes

- `ANTHROPIC_API_KEY` is server-side only — never bundled to the browser
- Passwords hashed with bcrypt (`passlib`)
- JWTs: 15-min access token + 7-day httpOnly refresh cookie
- Input sanitised with `bleach` before DB write
- CORS locked to `ALLOWED_ORIGINS`
- SQL Injection prevented by SQLAlchemy ORM (parameterised queries)

## Database Schema

```
users → posts → post_tags → tags
  └→ ai_usage_log
```

Migrations run automatically on container start via `alembic upgrade head`.

## Post-MVP Roadmap

- [ ] Streaming AI responses (SSE)
- [ ] Redis-backed JWT blocklist for true server-side logout
- [ ] Full-text search (`pg_trgm` / Typesense)
- [ ] Image uploads (S3/R2 presigned URLs)
- [ ] Post view analytics (Redis HyperLogLog)
- [ ] Threaded comments with moderation
