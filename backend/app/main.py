from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .modules.auth.router import router as auth_router
from .modules.posts.router import router as posts_router
from .modules.ai.router import router as ai_router

app = FastAPI(
    title="AI Blog Studio API",
    description="Backend API for AI Blog Studio — a markdown blog editor with AI writing tools.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
