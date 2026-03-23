from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .schemas import (
    ImproveRequest,
    ImproveResponse,
    SummaryRequest,
    SummaryResponse,
    TagsRequest,
    TagsResponse,
    SEOTitleRequest,
    SEOTitleResponse,
    TLDRRequest,
    TLDRResponse,
)
from .service import (
    improve_content,
    generate_summary,
    generate_tags,
    generate_seo_title,
    generate_tldr,
)
from .rate_limiter import check_rate_limit
from ..auth.router import get_current_user
from ...database import get_db

router = APIRouter()


@router.post("/improve", response_model=ImproveResponse)
async def improve(
    request: ImproveRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(str(current_user.id))
    return improve_content(db, str(current_user.id), request.content, request.context)


@router.post("/summary", response_model=SummaryResponse)
async def summary(
    request: SummaryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(str(current_user.id))
    return generate_summary(
        db, str(current_user.id), request.content, request.max_sentences
    )


@router.post("/tags", response_model=TagsResponse)
async def tags(
    request: TagsRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(str(current_user.id))
    return generate_tags(
        db, str(current_user.id), request.content, request.title, request.max_tags
    )


@router.post("/seo-title", response_model=SEOTitleResponse)
async def seo_title(
    request: SEOTitleRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(str(current_user.id))
    return generate_seo_title(
        db,
        str(current_user.id),
        request.content,
        request.title,
        request.target_keyword,
    )


@router.post("/tldr", response_model=TLDRResponse)
async def tldr(
    request: TLDRRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(str(current_user.id))
    return generate_tldr(db, str(current_user.id), request.content)
