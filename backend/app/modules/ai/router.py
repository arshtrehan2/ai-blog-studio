from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth.router import get_current_user_dep
from app.modules.ai import schemas, service
from app.modules.ai.rate_limiter import get_rate_limiter, RateLimiter
from app.modules.posts.service import log_ai_usage

router = APIRouter(prefix="/ai", tags=["ai"])


async def _check_rate_limit(current_user, rate_limiter: RateLimiter):
    allowed, retry_after = await rate_limiter.check(str(current_user.id))
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )


@router.post("/improve", response_model=schemas.ImproveResponse)
async def improve(
    data: schemas.ImproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    await _check_rate_limit(current_user, rate_limiter)
    try:
        improved, usage, latency = service.improve_content(data.content, data.context)
    except Exception:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI service timeout")
    await log_ai_usage(db, user_id=current_user.id, tool="improve",
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, latency_ms=latency)
    return schemas.ImproveResponse(improved_content=improved, model=service.settings.ANTHROPIC_MODEL, usage=usage)


@router.post("/summary", response_model=schemas.SummaryResponse)
async def summarize(
    data: schemas.SummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    await _check_rate_limit(current_user, rate_limiter)
    try:
        summary, usage, latency = service.generate_summary(data.content, data.max_sentences)
    except Exception:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI service timeout")
    await log_ai_usage(db, user_id=current_user.id, tool="summary",
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, latency_ms=latency)
    return schemas.SummaryResponse(summary=summary, model=service.settings.ANTHROPIC_MODEL, usage=usage)


@router.post("/tags", response_model=schemas.TagsResponse)
async def tags(
    data: schemas.TagsRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    await _check_rate_limit(current_user, rate_limiter)
    try:
        suggested_tags, usage, latency = service.suggest_tags(data.content, data.title, data.max_tags)
    except Exception:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI service timeout")
    await log_ai_usage(db, user_id=current_user.id, tool="tags",
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, latency_ms=latency)
    return schemas.TagsResponse(tags=suggested_tags, model=service.settings.ANTHROPIC_MODEL, usage=usage)


@router.post("/seo-title", response_model=schemas.SEOTitleResponse)
async def seo_title(
    data: schemas.SEOTitleRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    await _check_rate_limit(current_user, rate_limiter)
    try:
        seo_t, seo_d, usage, latency = service.generate_seo_title(data.content, data.title, data.target_keyword)
    except Exception:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI service timeout")
    await log_ai_usage(db, user_id=current_user.id, tool="seo-title",
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, latency_ms=latency)
    return schemas.SEOTitleResponse(seo_title=seo_t, seo_description=seo_d, model=service.settings.ANTHROPIC_MODEL, usage=usage)


@router.post("/tldr", response_model=schemas.TLDRResponse)
async def tldr(
    data: schemas.TLDRRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    await _check_rate_limit(current_user, rate_limiter)
    try:
        tldr_text, usage, latency = service.generate_tldr(data.content)
    except Exception:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI service timeout")
    await log_ai_usage(db, user_id=current_user.id, tool="tldr",
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, latency_ms=latency)
    return schemas.TLDRResponse(tldr=tldr_text, model=service.settings.ANTHROPIC_MODEL, usage=usage)
