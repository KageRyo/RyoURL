from pydantic import BaseModel, HttpUrl
from typing import Optional
import datetime

class UserSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    refresh: str

class TokenResponseSchema(BaseModel):
    access: str

class UserResponseSchema(BaseModel):
    username: str
    user_type: int
    access: str
    refresh: str
    
class UserInfoSchema(BaseModel):
    username: str
    user_type: int

class UrlSchema(BaseModel):
    origin_url: HttpUrl
    short_string: str
    short_url: HttpUrl
    create_date: datetime.datetime
    expire_date: Optional[datetime.datetime]
    visit_count: int
    creator_username: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            origin_url=obj.origin_url,
            short_string=obj.short_string,
            short_url=obj.short_url,
            create_date=obj.create_date,
            expire_date=obj.expire_date,
            visit_count=obj.visit_count,
            creator_username=obj.user.username if obj.user else None
        )

class ErrorSchema(BaseModel):
    detail: str

class UrlCreateSchema(BaseModel):
    origin_url: HttpUrl
    expire_date: Optional[datetime.datetime] = None

class CustomUrlCreateSchema(UrlCreateSchema):
    short_string: str