from typing import Any, List, Optional, Union
from uuid import uuid4
from schemas.url import UrlCreate
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder

from models.urls import Url as UrlModel
from .base import RepositoryDB, CreateSchemaType, ModelType
from core.config import settings


async def build_full_url(
    prefix_path: str,
    key: Union[str, int] = None
) -> str:
    if key is None:
        key = ''
    prefix_path = prefix_path.lstrip('/').rstrip('/')
    return 'http://{}:{}/{}/{}'.format(
        settings.project_host,
        settings.project_port,
        prefix_path,
        key
    )


class RepositoryUrl(RepositoryDB[UrlModel, UrlCreate]):
    @staticmethod
    async def short_url(short_id: str):
        prefix = '/api/v1/urls'
        return await build_full_url(prefix_path=prefix, key=short_id)

    async def get(
        self,
        db: AsyncSession,
        short_id: Any,
        used: bool = True
    ) -> Optional[ModelType]:
        short_url = await RepositoryUrl.short_url(short_id=short_id)
        statement = select(self._model).where(
            self._model.short_url == short_url
        )
        result = (await db.execute(statement=statement)).scalar_one_or_none()
        if result and not result.deleted and used:
            result.count_used += 1
            await db.commit()
        return result

    async def get_multi(
        self, db: AsyncSession, *, skip=0, limit=100
    ) -> List[ModelType]:
        statement = select(self._model).where(
            self._model.deleted == false()
        ).offset(skip).limit(limit)
        result = await db.execute(statement=statement)
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(self._model).where(
            self._model.url == obj_in_data['url']
        )
        result = await db.execute(statement=statement)
        response = result.scalar_one_or_none()
        if response is not None:
            return response
        obj_in_data['short_url'] = await RepositoryUrl.short_url(
            short_id=uuid4().hex
        )
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, short_id: str) -> ModelType:
        statement = select(self._model).where(self._model.id == short_id)
        result = await db.execute(statement=statement)
        db_obj = result.scalar_one_or_none()
        if db_obj is None or db_obj.deleted:
            return
        db_obj.deleted = True
        await db.commit()
        return db_obj


url_crud = RepositoryUrl(UrlModel)
