from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .url import router as url_router
from db.db import get_session

api_router = APIRouter()
api_router.include_router(
    url_router,
    prefix='/urls',
    tags=['URL\'s']
)


@api_router.get('/')
async def main():
    return {'status': 'OK'}


@api_router.get('/ping')
async def ping(db: AsyncSession = Depends(get_session)):
    q = text('SELECT 1;')

    result = {}
    try:
        await db.execute(statement=q)
    except OSError:
        result['db_status'] = False
    else:
        result['db_status'] = True
    return JSONResponse(content=result)
