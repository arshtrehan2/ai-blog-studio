# AI Blog Studio

A full-stack AI-powered blog platform built with Next.js and FastAPI, backed by PostgreSQL, Redis, and Anthropic Claude.

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), SQLAlchemy, Alembic
- **Database**: PostgreSQL 16
- **Cache / Rate-Limiting**: Redis 7
- **AI**: Anthropic Claude (`claude-3-5-sonnet`)
- **Auth**: JWT (HS256) + bcrypt

## Features

- 📝 Markdown editor with live preview
- 🤖 AI tools: Improve, Summary, Tags, SEO Title, TLDR
- 🔐 JWT authentication with refresh token rotation
- 🚦 Redis sliding-window rate limiting (20 AI req/user/hr)
- 🔍 SEO-optimised public blog feed (SSR)
- 🏷️ Tag management with slug-based URLs

## Quick Start

```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY & JWT_SECRET_KEY
docker compose up --build
```

| Service  | URL                      |
|----------|--------------------------|
| Frontend | http://localhost:3000    |
| Backend  | http://localhost:8000    |
| API Docs | http://localhost:8000/docs |

## Directory Structure

```
ai-blog-studio/
├── frontend/        # Next.js application
├── backend/         # FastAPI application
├── docker-compose.yml
└── .env.example
```
