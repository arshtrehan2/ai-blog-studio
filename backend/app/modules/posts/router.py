from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from .schemas import PostCreate, PostUpdate
from .service import (
    create_post,
    get_posts,
    get_post,
    update_post,
    delete_post,
    publish_post,
)
from ..auth.router import get_current_user, get_optional_current_user
from ...database import get_db

router = APIRouter()


def serialize_post(post) -> dict:
    return {
        "id": str(post.id),
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "tags": [t.name for t in post.tags],
        "status": post.status,
        "summary": post.summary,
        "seo_title": post.seo_title,
        "seo_description": post.seo_description,
        "author_id": str(post.author_id),
        "author": {
            "id": str(post.author.id),
            "display_name": post.author.display_name,
        },
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }


@router.post("", status_code=201)
async def create_new_post(
    post_data: PostCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = create_post(db, post_data, str(current_user.id))
    return serialize_post(post)


@router.get("")
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None),
    author_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    result = get_posts(db, page, page_size, tag, author_id)
    items = [
        {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "summary": p.summary,
            "tags": [t.name for t in p.tags],
            "author": {
                "id": str(p.author.id),
                "display_name": p.author.display_name,
            },
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
        }
        for p in result["items"]
    ]
    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    }


@router.get("/{post_id}")
async def get_single_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    post = get_post(db, post_id, current_user)
    return serialize_post(post)


@router.put("/{post_id}")
async def update_existing_post(
    post_id: str,
    post_data: PostUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = update_post(db, post_id, post_data, current_user)
    return serialize_post(post)


@router.delete("/{post_id}", status_code=204)
async def delete_existing_post(
    post_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_post(db, post_id, current_user)
    return None


@router.patch("/{post_id}/publish")
async def publish_existing_post(
    post_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = publish_post(db, post_id, current_user)
    return {
        "id": str(post.id),
        "status": post.status,
        "published_at": post.published_at.isoformat(),
        "slug": post.slug,
    }
