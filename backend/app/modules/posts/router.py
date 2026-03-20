import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user, get_optional_current_user
from app.modules.posts.schemas import (
    AuthorResponse,
    PostCreate,
    PostListItem,
    PostListResponse,
    PostUpdate,
)
from app.modules.posts.service import (
    create_post,
    delete_post,
    format_post_tags,
    get_post,
    get_posts,
    publish_post,
    update_post,
)

router = APIRouter()


def _post_dict(post) -> dict:
    """Serialize a Post ORM object to a plain dict for the response."""
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "tags": format_post_tags(post),
        "status": post.status,
        "summary": post.summary,
        "seo_title": post.seo_title,
        "seo_description": post.seo_description,
        "author_id": post.author_id,
        "author": (
            {"id": post.author.id, "display_name": post.author.display_name}
            if post.author
            else None
        ),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "published_at": post.published_at,
    }


@router.post("", status_code=201)
def create_new_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new blog post (draft by default)."""
    post = create_post(db, data, current_user)
    return _post_dict(post)


@router.get("", response_model=PostListResponse)
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None),
    author_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
):
    """List published posts — public, paginated, filterable by tag / author."""
    posts, total = get_posts(db, page=page, page_size=page_size, tag=tag, author_id=author_id)
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0

    items = [
        PostListItem(
            id=p.id,
            title=p.title,
            slug=p.slug,
            summary=p.summary,
            tags=format_post_tags(p),
            author=AuthorResponse(id=p.author.id, display_name=p.author.display_name),
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in posts
    ]
    return PostListResponse(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/{post_id}")
def get_single_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Get a post by UUID or slug. Published posts are public; drafts require ownership."""
    post = get_post(db, post_id, current_user)
    return _post_dict(post)


@router.put("/{post_id}")
def update_existing_post(
    post_id: str,
    data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full update of a post. Requires auth + ownership."""
    post = update_post(db, post_id, data, current_user)
    return _post_dict(post)


@router.delete("/{post_id}", status_code=204)
def delete_existing_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a post. Requires auth + ownership."""
    delete_post(db, post_id, current_user)


@router.patch("/{post_id}/publish")
def publish_existing_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Transition draft → published. Sets published_at timestamp."""
    post = publish_post(db, post_id, current_user)
    return {
        "id": post.id,
        "status": post.status,
        "published_at": post.published_at,
        "slug": post.slug,
    }
