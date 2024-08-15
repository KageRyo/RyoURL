from http import HTTPStatus
import random
import string
import datetime

from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from .auth import JWTAuth
from ..models import Url, User
from .schemas import UrlSchema, ErrorSchema, UrlCreateSchema

jwt_auth = JWTAuth()
short_url_router = Router(tags=["short-url"])

def generate_short_url(length=6):
    char = string.ascii_letters + string.digits
    while True:
        short_string = ''.join(random.choices(char, k=length))
        if not Url.objects.filter(short_string=short_string).exists():
            return short_string

def handle_domain(request, short_string):
    domain = request.build_absolute_uri('/').strip('/')
    return f'{domain}/{short_string}'

def create_url_entry(origin_url, short_string, short_url, expire_date=None, user=None):
    if user is None:
        user, _ = User.objects.get_or_create(username='anonymous', defaults={'user_type': 0})
    return Url.objects.create(
        origin_url=str(origin_url),
        short_string=short_string,
        short_url=str(short_url),
        create_date=datetime.datetime.now(),
        expire_date=expire_date,
        user=user
    )

@short_url_router.post("/short", response={HTTPStatus.CREATED: UrlSchema, HTTPStatus.BAD_REQUEST: ErrorSchema})
def create_short_url(request, data: UrlCreateSchema):
    short_string = generate_short_url()
    short_url = handle_domain(request, short_string)
    
    # 嘗試獲取認證信息，但不強制要求
    token = request.headers.get('Authorization', '').split(' ')[-1]
    auth = jwt_auth.authenticate(request, token) if token else None
    
    user = auth['user'] if auth else None

    url = create_url_entry(
        origin_url=data.origin_url,
        short_string=short_string,
        short_url=short_url,
        expire_date=data.expire_date,
        user=user
    )
    return HTTPStatus.CREATED, UrlSchema.from_orm(url)

@short_url_router.get("/origin/{short_string}", response={HTTPStatus.OK: UrlSchema, HTTPStatus.NOT_FOUND: ErrorSchema})
def get_original_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return HTTPStatus.OK, UrlSchema.from_orm(url)