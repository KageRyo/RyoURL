from http import HTTPStatus
import random
import string
import datetime

from django.http import Http404
from ninja import Router
from django.shortcuts import get_object_or_404

from ..models import Url, User
from schemas.schemas import UrlSchema, ErrorSchema, UrlCreateSchema

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
    try:
        short_string = generate_short_url()
        short_url = handle_domain(request, short_string)
        
        user = request.auth.get('user') if request.auth else None

        url = create_url_entry(
            origin_url=data.origin_url,
            short_string=short_string,
            short_url=short_url,
            expire_date=data.expire_date,
            user=user
        )
        
        return HTTPStatus.CREATED, UrlSchema.from_orm(url)
    except Exception as e:
        return HTTPStatus.BAD_REQUEST, ErrorSchema(detail=str(e))

@short_url_router.get("/origin/{short_string}", response={HTTPStatus.OK: UrlSchema, HTTPStatus.NOT_FOUND: ErrorSchema})
def get_original_url(request, short_string: str):
    try:
        url = get_object_or_404(Url, short_string=short_string)
        return HTTPStatus.OK, UrlSchema.from_orm(url)
    except Http404:
        return HTTPStatus.NOT_FOUND, ErrorSchema(detail="Short URL not found")