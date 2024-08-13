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
    access: str
    refresh: str

class UrlSchema(Schema):
    origin_url: HttpUrl
    short_string: str
    short_url: HttpUrl
    create_date: datetime.datetime
    expire_date: Optional[datetime.datetime]
    visit_count: int

class ErrorSchema(Schema):
    message: str

class UrlCreateSchema(Schema):
    origin_url: HttpUrl
    expire_date: Optional[datetime.datetime] = None

class CustomUrlCreateSchema(UrlCreateSchema):
    short_string: str