from uuid import uuid4
from schemas.url import UrlCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder

from models.urls import Url as UrlModel
from .base import RepositoryDB, CreateSchemaType, ModelType


class RepositoryUrl(RepositoryDB[UrlModel, UrlCreate]):
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


url_crud = RepositoryUrl(UrlModel)
