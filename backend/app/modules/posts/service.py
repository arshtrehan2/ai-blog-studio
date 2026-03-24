import uuid
import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from slugify import slugify

from app.modules.posts.models import Post, Tag, PostTag, AIUsageLog
from app.modules.posts.schemas import PostCreate, PostUpdate


def utcnow():
    return datetime.now(timezone.utc)


async def generate_unique_slug(db: AsyncSession, title: str, exclude_id: Optional[uuid.UUID] = None) -> str:
    base_slug = slugify(title)
    if not base_slug:
        base_slug = "post"

    candidate = base_slug
    counter = 1
    while True:
        query = select(Post).where(
            Post.slug == candidate,
            Post.deleted_at.is_(None),
        )
        if exclude_id:
            query = query.where(Post.id != exclude_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if not existing:
            return candidate
        suffix = str(uuid.uuid4())[:8]
        candidate = f"{base_slug}-{suffix}"
        counter += 1
        if counter > 10:
            # Fallback: use full UUID
            return f"{base_slug}-{uuid.uuid4().hex[:8]}"


async def get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    slug = slugify(name)
    if not slug:
        slug = "tag"
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name, slug=slug)
        db.add(tag)
        await db.flush()
        await db.refresh(tag)
    return tag


async def sync_tags(db: AsyncSession, post: Post, tag_names: list[str]) -> None:
    """Sync post tags: remove old, add new."""
    # Remove existing post_tags
    existing = await db.execute(
        select(PostTag).where(PostTag.post_id == post.id)
    )
    for pt in existing.scalars().all():
        await db.delete(pt)
    await db.flush()

    # Add new tags
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        tag = await get_or_create_tag(db, name)
        pt = PostTag(post_id=post.id, tag_id=tag.id)
        db.add(pt)
    await db.flush()


async def get_post_with_relations(db: AsyncSession, post_id: uuid.UUID) -> Optional[Post]:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.tags))
        .where(Post.id == post_id, Post.deleted_at.is_(None))
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def get_post_by_id_or_slug(db: AsyncSession, id_or_slug: str) -> Optional[Post]:
    """Get a post by UUID or slug."""
    query = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.tags))
        .where(Post.deleted_at.is_(None))
    )
    # Try UUID first
    try:
        post_id = uuid.UUID(id_or_slug)
        result = await db.execute(query.where(Post.id == post_id))
    except ValueError:
        result = await db.execute(query.where(Post.slug == id_or_slug))
    return result.scalar_one_or_none()


async def create_post(db: AsyncSession, author_id: uuid.UUID, payload: PostCreate) -> Post:
    slug = await generate_unique_slug(db, payload.title)
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
    await db.flush()
    await db.refresh(post)

    if payload.tags:
        await sync_tags(db, post, payload.tags)

    return await get_post_with_relations(db, post.id)


async def update_post(
    db: AsyncSession, post: Post, payload: PostUpdate, current_user_id: uuid.UUID
) -> Post:
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

    post.updated_at = utcnow()
    await db.flush()

    if payload.tags is not None:
        await sync_tags(db, post, payload.tags)

    return await get_post_with_relations(db, post.id)


async def delete_post(db: AsyncSession, post: Post, current_user_id: uuid.UUID) -> None:
    if post.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    post.deleted_at = utcnow()
    await db.flush()


async def publish_post(db: AsyncSession, post: Post, current_user_id: uuid.UUID) -> Post:
    if post.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if post.status == "published":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post is already published")
    post.status = "published"
    post.published_at = utcnow()
    post.updated_at = utcnow()
    await db.flush()
    return await get_post_with_relations(db, post.id)


async def list_published_posts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    tag: Optional[str] = None,
    author_id: Optional[uuid.UUID] = None,
) -> dict:
    query = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.tags))
        .where(Post.status == "published", Post.deleted_at.is_(None))
    )

    if tag:
        query = query.join(Post.tags).where(Tag.name == tag)

    if author_id:
        query = query.where(Post.author_id == author_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginate
    query = query.order_by(Post.published_at.desc())
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    posts = result.scalars().all()

    return {
        "items": posts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


async def log_ai_usage(
    db: AsyncSession,
    user_id: uuid.UUID,
    tool: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: Optional[int] = None,
    post_id: Optional[uuid.UUID] = None,
) -> None:
    log = AIUsageLog(
        user_id=user_id,
        tool=tool,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        post_id=post_id,
    )
    db.add(log)
    await db.flush()
