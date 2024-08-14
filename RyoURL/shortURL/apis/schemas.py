from ninja import Schema
from pydantic import HttpUrl
from typing import Optional
import datetime

class UserSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    refresh: str

class TokenResponseSchema(Schema):
    access: str

class UserResponseSchema(Schema):
    username: str
    user_type: int
    access: str
    refresh: str

class UrlSchema(Schema):
    origin_url: HttpUrl
    short_string: str
    short_url: HttpUrl
    create_date: datetime.datetime
    expire_date: Optional[datetime.datetime]
    visit_count: int
    creator_username: Optional[str] = None

    @classmethod
    def from_orm(cls, obj):
        data = {
            "origin_url": obj.origin_url,
            "short_string": obj.short_string,
            "short_url": obj.short_url,
            "create_date": obj.create_date,
            "expire_date": obj.expire_date,
            "visit_count": obj.visit_count,
            "creator_username": obj.user.username if obj.user and obj.user.username != 'anonymous' else None
        }
        return cls(**data)

class ErrorSchema(Schema):
    message: str

class UrlCreateSchema(Schema):
    origin_url: HttpUrl
    expire_date: Optional[datetime.datetime] = None

class CustomUrlCreateSchema(UrlCreateSchema):
    short_string: str