import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth.router import get_current_user_dep
from app.modules.auth.service import get_current_user
from app.modules.posts import schemas, service

router = APIRouter(prefix="/posts", tags=["posts"])

_optional_bearer_scheme = HTTPBearer(auto_error=False)


async def _optional_bearer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        return None
    return await get_current_user(credentials.credentials, db)


def _post_to_response(post) -> schemas.PostResponse:
    return schemas.PostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        tags=[t.name for t in post.tags],
        status=post.status,
        summary=post.summary,
        seo_title=post.seo_title,
        seo_description=post.seo_description,
        author_id=post.author_id,
        author=schemas.AuthorResponse.model_validate(post.author) if post.author else None,
        published_at=post.published_at,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


def _post_to_list_item(post) -> schemas.PostListItem:
    return schemas.PostListItem(
        id=post.id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        tags=[t.name for t in post.tags],
        author=schemas.AuthorResponse.model_validate(post.author) if post.author else None,
        published_at=post.published_at,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post("", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: schemas.PostCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
):
    post = await service.create_post(db, data, current_user.id)
    return _post_to_response(post)


@router.get("", response_model=schemas.PostListResponse)
async def list_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    tag: Optional[str] = Query(default=None),
    author_id: Optional[UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    posts, total = await service.list_posts(
        db, page=page, page_size=page_size, tag=tag, author_id=author_id
    )
    total_pages = max(1, math.ceil(total / page_size))
    return schemas.PostListResponse(
        items=[_post_to_list_item(p) for p in posts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{id}", response_model=schemas.PostResponse)
async def get_post(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(_optional_bearer),
):
    post = await service.get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status != "published":
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if post.author_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return _post_to_response(post)


@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(
    id: str,
    data: schemas.PostUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
):
    post = await service.get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    post = await service.update_post(db, post, data)
    return _post_to_response(post)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
):
    post = await service.get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    await service.delete_post(db, post)


@router.patch("/{id}/publish", response_model=schemas.PublishResponse)
async def publish_post(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_dep),
):
    post = await service.get_post_by_id_or_slug(db, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if post.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Post is already published"
        )
    post = await service.publish_post(db, post)
    return schemas.PublishResponse(
        id=post.id,
        status=post.status,
        published_at=post.published_at,
        slug=post.slug,
    )
