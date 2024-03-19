from sqlalchemy import Column, Integer
from sqlalchemy_utils import URLType

from .base import Base


class Url(Base):
    __tablename__ = 'URL'
    id = Column(Integer, primary_key=True)
    url = Column(URLType, unique=True, nullable=False)
    short_url = Column(URLType, unique=True, nullable=False)
