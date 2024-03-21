import uvicorn
from fastapi import FastAPI, status, Depends
from fastapi.responses import ORJSONResponse
from fastapi.requests import Request
from fastapi.exceptions import HTTPException

from core.config import settings
from api.v1.base import api_router


BLACK_LIST = [
    '127.0.0.5'
]


async def check_allowed_ip(request: Request):
    def is_ip_banned(headers):
        is_banned = False
        try:
            real_ip = headers['X-REAL-IP']
            is_banned = real_ip in BLACK_LIST
        except KeyError:
            is_banned = False
        return is_banned

    if is_ip_banned(request.headers):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


app = FastAPI(
    title=settings.app_title,
    docs_url='/api/v1/docs',
    default_response_class=ORJSONResponse,
)
app.include_router(
    api_router,
    prefix='/api/v1',
    dependencies=[Depends(check_allowed_ip)]
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.project_host,
        port=settings.project_port,
        reload=True
    )
