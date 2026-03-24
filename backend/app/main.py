from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.posts.router import router as posts_router
from app.modules.ai.router import router as ai_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(posts_router)
    app.include_router(ai_router)

    return app


app = create_app()
