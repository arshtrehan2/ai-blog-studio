from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.service import get_current_user
from app.modules.auth.models import User
from app.middleware.sanitizer import sanitize_html
from .rate_limiter import check_ai_rate_limit
from .service import (
    improve_content,
    generate_summary,
    suggest_tags,
    generate_seo_title,
    generate_tldr,
)
from .schemas import (
    ImproveRequest, ImproveResponse,
    SummaryRequest, SummaryResponse,
    TagsRequest, TagsResponse,
    SeoTitleRequest, SeoTitleResponse,
    TldrRequest, TldrResponse,
)

router = APIRouter()


def _rate_limit(current_user: User):
    check_ai_rate_limit(str(current_user.id))


@router.post("/improve", response_model=ImproveResponse)
def improve_endpoint(
    payload: ImproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _rate_limit(current_user)
    payload.content = sanitize_html(payload.content)
    return improve_content(db, current_user.id, payload)


@router.post("/summary", response_model=SummaryResponse)
def summary_endpoint(
    payload: SummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _rate_limit(current_user)
    payload.content = sanitize_html(payload.content)
    return generate_summary(db, current_user.id, payload)


@router.post("/tags", response_model=TagsResponse)
def tags_endpoint(
    payload: TagsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _rate_limit(current_user)
    payload.content = sanitize_html(payload.content)
    return suggest_tags(db, current_user.id, payload)


@router.post("/seo-title", response_model=SeoTitleResponse)
def seo_title_endpoint(
    payload: SeoTitleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _rate_limit(current_user)
    payload.content = sanitize_html(payload.content)
    return generate_seo_title(db, current_user.id, payload)


@router.post("/tldr", response_model=TldrResponse)
def tldr_endpoint(
    payload: TldrRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _rate_limit(current_user)
    payload.content = sanitize_html(payload.content)
    return generate_tldr(db, current_user.id, payload)
