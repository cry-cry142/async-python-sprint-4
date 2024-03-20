from typing import Any, List, Optional
from uuid import uuid4
from schemas.url import UrlCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder

from models.urls import Url as UrlModel
from .base import RepositoryDB, CreateSchemaType, ModelType


class RepositoryUrl(RepositoryDB[UrlModel, UrlCreate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await super().get(db, id)
        if not result.deleted:
            result.count_used += 1
            await db.commit()
        return result

    async def get_multi(self, db: AsyncSession, *, skip=0, limit=100) -> List[ModelType]:
        statement = select(self._model).where(self._model.deleted == False).offset(skip).limit(limit)
        result = await db.execute(statement=statement)
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(self._model).where(self._model.url == obj_in_data['url'])
        result = await db.execute(statement=statement)
        response = result.scalar_one_or_none()
        if response is not None:
            return response
        obj_in_data['short_url'] = 'http://short.me/{}'.format(uuid4().hex)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> ModelType:
        statement = select(self._model).where(self._model.id == id)
        result = await db.execute(statement=statement)
        # db_obj = result.scalar_one_or_none()
        db_obj = result.scalar_one_or_none()
        if db_obj is None or db_obj.deleted:
            return
        db_obj.deleted = True
        await db.commit()
        return db_obj


url_crud = RepositoryUrl(UrlModel)
