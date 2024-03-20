from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from schemas import url as url_schema
from services.url import url_crud


router = APIRouter()


@router.get('/', response_model=List[url_schema.Url])
async def read_urls(
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    urls = await url_crud.get_multi(db=db, skip=skip, limit=limit)
    return urls


@router.get('/{id}', response_model=url_schema.Url)
async def read_url(
    *,
    db: AsyncSession = Depends(get_session),
    id: int,
) -> Any:
    url = await url_crud.get(db=db, id=id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item not found'
        )
    return url


@router.post(
    '/',
    response_model=url_schema.Url,
    status_code=status.HTTP_201_CREATED
)
async def create_url(
    url_in: url_schema.UrlCreate,
    *,
    db: AsyncSession = Depends(get_session),
) -> Any:
    url = await url_crud.create(db=db, obj_in=url_in)
    return url


@router.delete('/{id}')
async def delete_url(
    id: int,
    db: AsyncSession = Depends(get_session),
):
    url = await url_crud.delete(db=db, id=id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item not found'
        )
    return url
