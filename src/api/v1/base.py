from fastapi import APIRouter

from .url import router as url_router

api_router = APIRouter()
api_router.include_router(
    url_router,
    prefix='/urls',
    tags=['URL\'s']
)


@api_router.get('/')
async def main():
    return {'status': 'OK'}
