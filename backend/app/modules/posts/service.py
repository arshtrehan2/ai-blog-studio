import uuid as uuid_lib
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from slugify import slugify
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from .models import Post, Tag, PostTag
from .schemas import PostCreate, PostUpdate


def utcnow():
    return datetime.now(timezone.utc)


# ── Slug helpers ────────────────────────────────────────────────────────────────

def _generate_slug(db: Session, title: str) -> str:
    base = slugify(title, max_length=270)
    slug = base
    if not _slug_taken(db, slug):
        return slug
    # Append short UUID suffix on collision
    suffix = str(uuid_lib.uuid4())[:8]
    return f"{base}-{suffix}"


def _slug_taken(db: Session, slug: str) -> bool:
    return (
        db.query(Post)
        .filter(Post.slug == slug, Post.deleted_at.is_(None))
        .first()
    ) is not None


# ── Tag helpers ────────────────────────────────────────────────────────────────

def _upsert_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    tags = []
    for name in tag_names:
        name = name.lower().strip()
        if not name:
            continue
        tag_slug = slugify(name)
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name, slug=tag_slug)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def _set_post_tags(db: Session, post: Post, tag_names: list[str]) -> None:
    # Remove old associations
    db.query(PostTag).filter(PostTag.post_id == post.id).delete()
    tags = _upsert_tags(db, tag_names)
    for tag in tags:
        pt = PostTag(post_id=post.id, tag_id=tag.id)
        db.add(pt)


# ── Query helpers ─────────────────────────────────────────────────────────────

def _base_post_query(db: Session):
    return (
        db.query(Post)
        .options(joinedload(Post.author), joinedload(Post.post_tags).joinedload(PostTag.tag))
        .filter(Post.deleted_at.is_(None))
    )


def get_post_or_404(db: Session, post_id_or_slug: str) -> Post:
    """Accept either a UUID or a slug string."""
    query = _base_post_query(db)
    try:
        pid = UUID(post_id_or_slug)
        post = query.filter(Post.id == pid).first()
    except ValueError:
        post = query.filter(Post.slug == post_id_or_slug).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


# ── CRUD ───────────────────────────────────────────────────────────────────

def create_post(db: Session, payload: PostCreate, author_id: UUID) -> Post:
    slug = _generate_slug(db, payload.title)
    post = Post(
        author_id=author_id,
        title=payload.title,
        slug=slug,
        content=payload.content,
        status=payload.status,
        summary=payload.summary,
        seo_title=payload.seo_title,
        seo_description=payload.seo_description,
    )
    if payload.status == "published":
        post.published_at = utcnow()
    db.add(post)
    db.flush()
    _set_post_tags(db, post, payload.tags)
    db.commit()
    db.refresh(post)
    return post


def list_posts(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    tag: Optional[str] = None,
    author_id: Optional[UUID] = None,
) -> dict:
    query = (
        _base_post_query(db)
        .filter(Post.status == "published")
        .order_by(Post.published_at.desc())
    )
    if tag:
        query = query.join(Post.post_tags).join(PostTag.tag).filter(Tag.name == tag.lower())
    if author_id:
        query = query.filter(Post.author_id == author_id)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = max(1, (total + page_size - 1) // page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


def get_post(
    db: Session,
    post_id_or_slug: str,
    current_user_id: Optional[UUID] = None,
) -> Post:
    post = get_post_or_404(db, post_id_or_slug)
    if post.status != "published":
        if current_user_id is None or post.author_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return post


def update_post(
    db: Session,
    post_id: str,
    payload: PostUpdate,
    current_user_id: UUID,
) -> Post:
    post = get_post_or_404(db, post_id)
    if post.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    if payload.summary is not None:
        post.summary = payload.summary
    if payload.seo_title is not None:
        post.seo_title = payload.seo_title
    if payload.seo_description is not None:
        post.seo_description = payload.seo_description
    if payload.tags is not None:
        _set_post_tags(db, post, payload.tags)

    post.updated_at = utcnow()
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: str, current_user_id: UUID) -> None:
    post = get_post_or_404(db, post_id)
    if post.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    post.deleted_at = utcnow()
    db.commit()


def publish_post(db: Session, post_id: str, current_user_id: UUID) -> Post:
    post = get_post_or_404(db, post_id)
    if post.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if post.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Post is already published"
        )
    post.status = "published"
    post.published_at = utcnow()
    db.commit()
    db.refresh(post)
    return post
