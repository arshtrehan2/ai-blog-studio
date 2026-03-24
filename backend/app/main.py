from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.modules.auth.router import router as auth_router
from app.modules.posts.router import router as posts_router
from app.modules.ai.router import router as ai_router

settings = get_settings()

app = FastAPI(
    title="AI Blog Studio API",
    description="Backend API for AI Blog Studio",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(ai_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
