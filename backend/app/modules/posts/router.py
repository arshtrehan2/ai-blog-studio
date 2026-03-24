from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.service import get_current_user
from app.modules.auth.models import User
from .schemas import PostCreate, PostUpdate, PostOut, PaginatedPosts, PostListItem, PublishResponse
from .service import create_post, list_posts, get_post, update_post, delete_post, publish_post
from app.middleware.sanitizer import sanitize_html

router = APIRouter()


def _to_post_out(post) -> PostOut:
    return PostOut(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        tags=post.tags,
        status=post.status,
        summary=post.summary,
        seo_title=post.seo_title,
        seo_description=post.seo_description,
        author_id=post.author_id,
        author=post.author,
        published_at=post.published_at,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post("", response_model=PostOut, status_code=201)
def create_post_endpoint(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload.content = sanitize_html(payload.content)
    post = create_post(db, payload, current_user.id)
    return _to_post_out(post)


@router.get("", response_model=PaginatedPosts)
def list_posts_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None),
    author_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
):
    result = list_posts(db, page=page, page_size=page_size, tag=tag, author_id=author_id)
    items = [
        PostListItem(
            id=p.id,
            title=p.title,
            slug=p.slug,
            summary=p.summary,
            tags=p.tags,
            author=p.author,
            published_at=p.published_at,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in result["items"]
    ]
    return PaginatedPosts(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


@router.get("/{post_id}", response_model=PostOut)
def get_post_endpoint(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(
        lambda credentials=Depends(__import__('fastapi').security.HTTPBearer(auto_error=False)),
        db=Depends(get_db): None
    ),
):
    # Try to resolve current user if token present
    from app.modules.auth.service import bearer_scheme, decode_token, get_user_by_id
    from fastapi import Request
    # Inline resolution to allow optional auth
    return _get_post_with_optional_auth(post_id, db)


def _get_post_with_optional_auth(post_id: str, db: Session, user_id: Optional[UUID] = None):
    post = get_post(db, post_id, current_user_id=user_id)
    return _to_post_out(post)


@router.get("/{post_id}/detail", response_model=PostOut, include_in_schema=False)
def get_post_detail(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    user_id = current_user.id if current_user else None
    post = get_post(db, post_id, current_user_id=user_id)
    return _to_post_out(post)


@router.put("/{post_id}", response_model=PostOut)
def update_post_endpoint(
    post_id: str,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.content:
        payload.content = sanitize_html(payload.content)
    post = update_post(db, post_id, payload, current_user.id)
    return _to_post_out(post)


@router.delete("/{post_id}", status_code=204)
def delete_post_endpoint(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_post(db, post_id, current_user.id)


@router.patch("/{post_id}/publish", response_model=PublishResponse)
def publish_post_endpoint(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = publish_post(db, post_id, current_user.id)
    return PublishResponse(
        id=post.id,
        status=post.status,
        published_at=post.published_at,
        slug=post.slug,
    )
