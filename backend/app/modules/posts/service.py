import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException
from slugify import slugify
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.posts.models import AIUsageLog, Post, PostTag, Tag
from app.modules.posts.schemas import PostCreate, PostUpdate


# ── Helpers ─────────────────────────────────────────────────────────────────

def _generate_slug(title: str, db: Session) -> str:
    base = slugify(title)
    slug = base
    collision = db.query(Post).filter(
        Post.slug == slug, Post.deleted_at.is_(None)
    ).first()
    if collision:
        slug = f"{base}-{str(uuid.uuid4())[:8]}"
    return slug


def _get_or_create_tag(db: Session, name: str) -> Tag:
    name = name.lower().strip()
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        tag = Tag(name=name, slug=slugify(name))
        db.add(tag)
        db.flush()
    return tag


def _set_post_tags(db: Session, post: Post, tag_names: List[str]) -> None:
    db.query(PostTag).filter(PostTag.post_id == post.id).delete()
    for name in tag_names:
        tag = _get_or_create_tag(db, name)
        db.add(PostTag(post_id=post.id, tag_id=tag.id))


def format_post_tags(post: Post) -> List[str]:
    return [t.name for t in post.tags]


# ── CRUD ───────────────────────────────────────────────────────────────────

def create_post(db: Session, data: PostCreate, author: User) -> Post:
    slug = _generate_slug(data.title, db)
    post = Post(
        author_id=author.id,
        title=data.title,
        slug=slug,
        content=data.content,
        status=data.status,
        summary=data.summary,
        seo_title=data.seo_title,
        seo_description=data.seo_description,
    )
    if data.status == "published":
        post.published_at = datetime.utcnow()

    db.add(post)
    db.flush()

    if data.tags:
        _set_post_tags(db, post, data.tags)

    db.commit()
    db.refresh(post)
    return post


def get_posts(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    tag: Optional[str] = None,
    author_id: Optional[uuid.UUID] = None,
) -> Tuple[List[Post], int]:
    q = db.query(Post).filter(
        Post.status == "published", Post.deleted_at.is_(None)
    )
    if tag:
        q = q.join(Post.tags).filter(Tag.slug == slugify(tag))
    if author_id:
        q = q.filter(Post.author_id == author_id)

    total = q.count()
    posts = (
        q.order_by(Post.published_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return posts, total


def get_post(db: Session, post_id: str, current_user: Optional[User] = None) -> Post:
    """Fetch by UUID or slug. Drafts require auth + ownership."""
    post: Optional[Post] = None
    try:
        uid = uuid.UUID(post_id)
        post = db.query(Post).filter(
            Post.id == uid, Post.deleted_at.is_(None)
        ).first()
    except ValueError:
        post = db.query(Post).filter(
            Post.slug == post_id, Post.deleted_at.is_(None)
        ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status == "draft":
        if not current_user or post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return post


def update_post(
    db: Session, post_id: str, data: PostUpdate, current_user: User
) -> Post:
    post = get_post(db, post_id, current_user)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_data = data.model_dump(exclude_unset=True)
    if "tags" in update_data:
        _set_post_tags(db, post, update_data.pop("tags") or [])

    for key, value in update_data.items():
        setattr(post, key, value)

    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: str, current_user: User) -> None:
    post = get_post(db, post_id, current_user)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    post.deleted_at = datetime.utcnow()
    db.commit()


def publish_post(db: Session, post_id: str, current_user: User) -> Post:
    try:
        uid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")

    post = db.query(Post).filter(
        Post.id == uid, Post.deleted_at.is_(None)
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if post.status == "published":
        raise HTTPException(status_code=400, detail="Post is already published")

    post.status = "published"
    post.published_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post
