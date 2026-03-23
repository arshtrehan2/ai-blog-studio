import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from slugify import slugify
from datetime import datetime
from typing import Optional, List
from .models import Post, Tag
from .schemas import PostCreate, PostUpdate
from ...middleware.sanitizer import sanitize_content


def generate_slug(title: str, db: Session) -> str:
    base_slug = slugify(title)
    slug = base_slug
    while (
        db.query(Post)
        .filter(Post.slug == slug, Post.deleted_at.is_(None))
        .first()
    ):
        slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
    return slug


def get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    tags = []
    for name in tag_names:
        name = name.lower().strip()
        if not name:
            continue
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name, slug=slugify(name))
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def create_post(db: Session, post_data: PostCreate, author_id: str) -> Post:
    sanitized_content = sanitize_content(post_data.content)
    slug = generate_slug(post_data.title, db)

    post = Post(
        author_id=author_id,
        title=post_data.title,
        slug=slug,
        content=sanitized_content,
        status=post_data.status,
        summary=post_data.summary,
        seo_title=post_data.seo_title,
        seo_description=post_data.seo_description,
    )

    if post_data.tags:
        post.tags = get_or_create_tags(db, post_data.tags)

    if post_data.status == "published":
        post.published_at = datetime.utcnow()

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_posts(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    tag: Optional[str] = None,
    author_id: Optional[str] = None,
) -> dict:
    query = db.query(Post).filter(
        Post.status == "published",
        Post.deleted_at.is_(None),
    )

    if tag:
        query = query.join(Post.tags).filter(Tag.name == tag)

    if author_id:
        query = query.filter(Post.author_id == author_id)

    total = query.count()
    posts = (
        query.order_by(Post.published_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": posts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


def get_post(db: Session, post_id: str, current_user=None) -> Post:
    try:
        uid = uuid.UUID(post_id)
        post = (
            db.query(Post)
            .filter(Post.id == uid, Post.deleted_at.is_(None))
            .first()
        )
    except ValueError:
        post = (
            db.query(Post)
            .filter(Post.slug == post_id, Post.deleted_at.is_(None))
            .first()
        )

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status != "published":
        if not current_user or str(post.author_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

    return post


def update_post(
    db: Session, post_id: str, post_data: PostUpdate, current_user
) -> Post:
    post = get_post(db, post_id, current_user)

    if str(post.author_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = sanitize_content(post_data.content)
    if post_data.summary is not None:
        post.summary = post_data.summary
    if post_data.seo_title is not None:
        post.seo_title = post_data.seo_title
    if post_data.seo_description is not None:
        post.seo_description = post_data.seo_description
    if post_data.tags is not None:
        post.tags = get_or_create_tags(db, post_data.tags)

    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: str, current_user) -> None:
    post = get_post(db, post_id, current_user)

    if str(post.author_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    post.deleted_at = datetime.utcnow()
    db.commit()


def publish_post(db: Session, post_id: str, current_user) -> Post:
    post = get_post(db, post_id, current_user)

    if str(post.author_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    if post.status == "published":
        raise HTTPException(status_code=400, detail="Post is already published")

    post.status = "published"
    post.published_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post
