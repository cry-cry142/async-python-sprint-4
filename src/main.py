import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import settings
from api.v1.base import router

app = FastAPI(
    title=settings.app_title,
    docs_url='/api/v1/docs',
    default_response_class=ORJSONResponse,
)
app.include_router(router, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.project_host,
        port=settings.project_port,
        reload=True
    )
