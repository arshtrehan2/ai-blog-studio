from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .modules.auth.router import router as auth_router
from .modules.posts.router import router as posts_router
from .modules.ai.router import router as ai_router

settings = get_settings()

app = FastAPI(
    title="AI Blog Studio API",
    description="Backend API for AI Blog Studio — a Next.js + FastAPI blog platform with AI writing tools.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
