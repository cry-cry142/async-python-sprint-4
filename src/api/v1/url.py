from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from models.urls import Url
from db.db import get_session
from schemas import url as url_schema
from services.url import url_crud


router = APIRouter()


async def is_deleted(obj: Url):
    if obj and obj.deleted:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail='Item has been deleted'
        )


@router.get('/', response_model=List[url_schema.Url])
async def read_urls(
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    urls = await url_crud.get_multi(db=db, skip=skip, limit=limit)
    return urls


@router.get('/{short_id}')
async def read_url(
    *,
    db: AsyncSession = Depends(get_session),
    short_id: str,
) -> Any:
    url = await url_crud.get(db=db, short_id=short_id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item not found'
        )
    await is_deleted(url)
    resp = Response(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        headers={'Location': url.url}
    )
    return resp


@router.get('/{short_id}/status')
async def status_url(
    *,
    db: AsyncSession = Depends(get_session),
    short_id: str
) -> Any:
    url = await url_crud.get(db=db, short_id=short_id, used=False)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item not found'
        )
    result = {}
    result['count_used'] = url.count_used
    try:
        await is_deleted(url)
    except HTTPException:
        result['status'] = 'deleted'
    else:
        result['status'] = 'exists'
    return JSONResponse(content=result)


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
    await is_deleted(url)
    return url


@router.delete('/{short_id}')
async def delete_url(
    short_id: str,
    db: AsyncSession = Depends(get_session),
):
    url = await url_crud.delete(db=db, short_id=short_id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item not found'
        )
    return url
