import uuid
from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.ai.rate_limiter import check_rate_limit, get_redis
from app.modules.ai.schemas import (
    ImproveRequest, ImproveResponse,
    SummaryRequest, SummaryResponse,
    TagsRequest, TagsResponse,
    SEOTitleRequest, SEOTitleResponse,
    TLDRRequest, TLDRResponse,
    UsageInfo,
)
from app.modules.ai.service import (
    improve_content, summarize_content, suggest_tags,
    generate_seo_title, generate_tldr,
)

router = APIRouter(prefix="/ai", tags=["ai"])


async def enforce_rate_limit(user_id: uuid.UUID, redis: aioredis.Redis):
    allowed, retry_after = await check_rate_limit(user_id, redis)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )


@router.post("/improve", response_model=ImproveResponse)
async def improve(
    payload: ImproveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await enforce_rate_limit(current_user.id, redis)
    result = await improve_content(payload.content, payload.context, current_user.id, db)
    return ImproveResponse(
        improved_content=result["improved_content"],
        model=result["model"],
        usage=UsageInfo(**result["usage"]),
    )


@router.post("/summary", response_model=SummaryResponse)
async def summary(
    payload: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await enforce_rate_limit(current_user.id, redis)
    result = await summarize_content(payload.content, payload.max_sentences, current_user.id, db)
    return SummaryResponse(
        summary=result["summary"],
        model=result["model"],
        usage=UsageInfo(**result["usage"]),
    )


@router.post("/tags", response_model=TagsResponse)
async def tags(
    payload: TagsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await enforce_rate_limit(current_user.id, redis)
    result = await suggest_tags(payload.content, payload.title, payload.max_tags, current_user.id, db)
    return TagsResponse(
        tags=result["tags"],
        model=result["model"],
        usage=UsageInfo(**result["usage"]),
    )


@router.post("/seo-title", response_model=SEOTitleResponse)
async def seo_title(
    payload: SEOTitleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await enforce_rate_limit(current_user.id, redis)
    result = await generate_seo_title(
        payload.content, payload.title, payload.target_keyword, current_user.id, db
    )
    return SEOTitleResponse(
        seo_title=result["seo_title"],
        seo_description=result["seo_description"],
        model=result["model"],
        usage=UsageInfo(**result["usage"]),
    )


@router.post("/tldr", response_model=TLDRResponse)
async def tldr(
    payload: TLDRRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await enforce_rate_limit(current_user.id, redis)
    result = await generate_tldr(payload.content, current_user.id, db)
    return TLDRResponse(
        tldr=result["tldr"],
        model=result["model"],
        usage=UsageInfo(**result["usage"]),
    )
