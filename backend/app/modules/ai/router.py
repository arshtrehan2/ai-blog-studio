from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.ai.rate_limiter import check_rate_limit
from app.modules.ai.schemas import (
    ImproveRequest,
    ImproveResponse,
    SEOTitleRequest,
    SEOTitleResponse,
    SummaryRequest,
    SummaryResponse,
    TagsRequest,
    TagsResponse,
    TLDRRequest,
    TLDRResponse,
)
from app.modules.ai.service import (
    generate_seo_title,
    generate_summary,
    generate_tldr,
    improve_content,
    suggest_tags,
)
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user

router = APIRouter()


@router.post("/improve", response_model=ImproveResponse)
def ai_improve(
    req: ImproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rewrite content for clarity & quality. Rate-limited: 20 req/user/hr."""
    check_rate_limit(str(current_user.id))
    return improve_content(db, current_user, req.content, req.context)


@router.post("/summary", response_model=SummaryResponse)
def ai_summary(
    req: SummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a concise article summary. Rate-limited: 20 req/user/hr."""
    check_rate_limit(str(current_user.id))
    return generate_summary(db, current_user, req.content, req.max_sentences)


@router.post("/tags", response_model=TagsResponse)
def ai_tags(
    req: TagsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Suggest relevant tags for the post. Rate-limited: 20 req/user/hr."""
    check_rate_limit(str(current_user.id))
    return suggest_tags(db, current_user, req.content, req.title, req.max_tags)


@router.post("/seo-title", response_model=SEOTitleResponse)
def ai_seo_title(
    req: SEOTitleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate SEO-optimised title + meta description. Rate-limited: 20 req/user/hr."""
    check_rate_limit(str(current_user.id))
    return generate_seo_title(db, current_user, req.content, req.title, req.target_keyword)


@router.post("/tldr", response_model=TLDRResponse)
def ai_tldr(
    req: TLDRRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a 1-2 sentence TLDR. Rate-limited: 20 req/user/hr."""
    check_rate_limit(str(current_user.id))
    return generate_tldr(db, current_user, req.content)
