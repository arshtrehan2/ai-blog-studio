import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user, decode_access_token, get_user_by_id
from app.modules.posts.schemas import (
    PostCreate, PostUpdate, PostResponse, PaginatedPostsResponse,
    PostListItem, AuthorInfo, PublishResponse,
)
from app.modules.posts.service import (
    create_post, update_post, delete_post, publish_post,
    list_published_posts, get_post_by_id_or_slug,
)

router = APIRouter(prefix="/posts", tags=["posts"])
optional_bearer = HTTPBearer(auto_error=False)


def _build_list_item(post) -> PostListItem:
    return PostListItem(
        id=post.id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        tags=[tag.name for tag in post.tags] if post.tags else [],
        author=AuthorInfo.model_validate(post.author),
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    token_data = decode_access_token(credentials.credentials)
    if not token_data:
        return None
    user = await get_user_by_id(db, uuid.UUID(token_data.user_id))
    return user if user and user.is_active else None


@router.post("", response_model=PostResponse, status_code=201)
async def create_new_post(
    payload: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await create_post(db, current_user.id, payload)
    return PostResponse.from_post(post)


@router.get("", response_model=PaginatedPostsResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None),
    author_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await list_published_posts(db, page=page, page_size=page_size, tag=tag, author_id=author_id)
    return PaginatedPostsResponse(
        items=[_build_list_item(p) for p in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


@router.get("/{id}", response_model=PostResponse)
async def get_post(
    id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Draft posts require auth + ownership
    if post.status != "published":
        if not current_user or post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return PostResponse.from_post(post)


@router.put("/{id}", response_model=PostResponse)
async def update_existing_post(
    id: str,
    payload: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    updated = await update_post(db, post, payload, current_user.id)
    return PostResponse.from_post(updated)


@router.delete("/{id}", status_code=204)
async def delete_existing_post(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    await delete_post(db, post, current_user.id)


@router.patch("/{id}/publish", response_model=PublishResponse)
async def publish_existing_post(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    published = await publish_post(db, post, current_user.id)
    return PublishResponse(
        id=published.id,
        status=published.status,
        published_at=published.published_at,
        slug=published.slug,
    )
