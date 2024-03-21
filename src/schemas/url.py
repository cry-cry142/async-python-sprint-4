from pydantic import BaseModel, HttpUrl


class UrlBase(BaseModel):
    url: HttpUrl


class UrlCreate(UrlBase):
    pass


class UrlInDBBase(UrlBase):
    id: int
    url: HttpUrl
    short_url: HttpUrl

    class Config:
        orm_mode = True


class Url(UrlInDBBase):
    pass
