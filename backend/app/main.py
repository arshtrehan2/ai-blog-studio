from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .modules.auth.router import router as auth_router
from .modules.posts.router import router as posts_router
from .modules.ai.router import router as ai_router

# Import models to register them with Base.metadata
from .modules.auth import models as auth_models  # noqa: F401
from .modules.posts import models as posts_models  # noqa: F401
from .modules.ai import models as ai_models  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Blog Studio API",
        version="1.0.0",
        description="FastAPI backend for AI Blog Studio",
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
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
