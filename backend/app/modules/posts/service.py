import math
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime, timezone

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete, insert
from sqlalchemy.orm import selectinload
import shortuuid

from app.modules.posts.models import Post, Tag, AIUsageLog, post_tags
from app.modules.posts.schemas import PostCreateRequest, PostUpdateRequest


def _generate_slug(title: str) -> str:
    base = slugify(title)
    if not base:
        base = "untitled"
    return base


async def _ensure_unique_slug(db: AsyncSession, base_slug: str, exclude_id: Optional[UUID] = None) -> str:
    slug = base_slug
    while True:
        query = select(Post).where(
            and_(Post.slug == slug, Post.deleted_at.is_(None))
        )
        if exclude_id:
            query = query.where(Post.id != exclude_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if not existing:
            return slug
        slug = f"{base_slug}-{shortuuid.ShortUUID().random(length=6).lower()}"


async def _get_or_create_tags(db: AsyncSession, tag_names: List[str]) -> List[Tag]:
    tags = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        tag_slug = slugify(name)
        result = await db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalar_one_or_none()
        if not tag:
            tag = Tag(name=name, slug=tag_slug)
            db.add(tag)
            await db.flush()
            await db.refresh(tag)
        tags.append(tag)
    return tags


async def _set_post_tags(db: AsyncSession, post_id: UUID, tag_names: List[str]) -> None:
    """Replace all tags for a post using explicit join-table management."""
    await db.execute(delete(post_tags).where(post_tags.c.post_id == post_id))
    if not tag_names:
        return
    tags = await _get_or_create_tags(db, tag_names)
    if tags:
        await db.execute(
            insert(post_tags),
            [{"post_id": post_id, "tag_id": tag.id} for tag in tags],
        )


async def _load_post_full(db: AsyncSession, post_id: UUID) -> Optional[Post]:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.tags), selectinload(Post.author))
        .where(and_(Post.id == post_id, Post.deleted_at.is_(None)))
    )
    return result.scalar_one_or_none()


async def create_post(db: AsyncSession, data: PostCreateRequest, author_id: UUID) -> Post:
    base_slug = _generate_slug(data.title)
    slug = await _ensure_unique_slug(db, base_slug)
    post = Post(
        author_id=author_id,
        title=data.title,
        slug=slug,
        content=data.content,
        status=data.status.value,
        summary=data.summary,
        seo_title=data.seo_title,
        seo_description=data.seo_description,
        published_at=datetime.now(timezone.utc) if data.status.value == "published" else None,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    if data.tags:
        await _set_post_tags(db, post.id, data.tags)
    return await _load_post_full(db, post.id)


async def get_post_by_id_or_slug(db: AsyncSession, id_or_slug: str) -> Optional[Post]:
    try:
        uid = UUID(id_or_slug)
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.tags), selectinload(Post.author))
            .where(and_(Post.id == uid, Post.deleted_at.is_(None)))
        )
        post = result.scalar_one_or_none()
        if post:
            return post
    except ValueError:
        pass
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.tags), selectinload(Post.author))
        .where(and_(Post.slug == id_or_slug, Post.deleted_at.is_(None)))
    )
    return result.scalar_one_or_none()


async def list_posts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    tag: Optional[str] = None,
    author_id: Optional[UUID] = None,
) -> Tuple[List[Post], int]:
    query = (
        select(Post)
        .options(selectinload(Post.tags), selectinload(Post.author))
        .where(and_(Post.status == "published", Post.deleted_at.is_(None)))
    )
    if tag:
        tag_slug = slugify(tag)
        query = query.join(Post.tags).where(Tag.slug == tag_slug)
    if author_id:
        query = query.where(Post.author_id == author_id)
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    offset = (page - 1) * page_size
    query = query.order_by(Post.published_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    posts = result.scalars().unique().all()
    return list(posts), total


async def update_post(db: AsyncSession, post: Post, data: PostUpdateRequest) -> Post:
    if data.title is not None:
        post.title = data.title
        if post.status != "published":
            base_slug = _generate_slug(data.title)
            post.slug = await _ensure_unique_slug(db, base_slug, exclude_id=post.id)
    if data.content is not None:
        post.content = data.content
    if data.summary is not None:
        post.summary = data.summary
    if data.seo_title is not None:
        post.seo_title = data.seo_title
    if data.seo_description is not None:
        post.seo_description = data.seo_description
    await db.flush()
    if data.tags is not None:
        await _set_post_tags(db, post.id, data.tags)
    return await _load_post_full(db, post.id)


async def delete_post(db: AsyncSession, post: Post) -> None:
    post.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def publish_post(db: AsyncSession, post: Post) -> Post:
    if post.status == "published":
        return post
    post.status = "published"
    post.published_at = datetime.now(timezone.utc)
    await db.flush()
    return await _load_post_full(db, post.id)


async def log_ai_usage(
    db: AsyncSession,
    user_id: UUID,
    tool: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: Optional[int] = None,
    post_id: Optional[UUID] = None,
) -> None:
    log = AIUsageLog(
        user_id=user_id,
        tool=tool,
        input_tokens=str(input_tokens),
        output_tokens=str(output_tokens),
        latency_ms=str(latency_ms) if latency_ms is not None else None,
        post_id=post_id,
    )
    db.add(log)
    await db.flush()
