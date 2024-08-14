import random
import string
import datetime

from ninja import Router
from django.shortcuts import get_object_or_404
from rest_framework import status

from .auth import JWTAuth
from ..models import Url
from .schemas import UrlSchema, ErrorSchema, UrlCreateSchema

short_url_auth = JWTAuth()
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
    return Url.objects.create(
        origin_url=str(origin_url),
        short_string=short_string,
        short_url=str(short_url),
        create_date=datetime.datetime.now(),
        expire_date=expire_date,
        user=user
    )

@short_url_router.post("/short", response={status.HTTP_201_CREATED: UrlSchema, status.HTTP_400_BAD_REQUEST: ErrorSchema})
def create_short_url(request, data: UrlCreateSchema):
    short_string = generate_short_url()
    short_url = handle_domain(request, short_string)
    
    try:
        auth = short_url_auth.authenticate(request, request.headers.get('Authorization', '').split(' ')[-1])
        user = auth['user']

        url = create_url_entry(
            origin_url=data.origin_url,
            short_string=short_string,
            short_url=short_url,
            expire_date=data.expire_date,
            user=user
        )
        return status.HTTP_201_CREATED, UrlSchema.from_orm(url)
    except Exception as e:
        return status.HTTP_400_BAD_REQUEST, ErrorSchema(message=str(e))

@short_url_router.get("/origin/{short_string}", response={status.HTTP_200_OK: UrlSchema, status.HTTP_404_NOT_FOUND: ErrorSchema})
def get_original_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return status.HTTP_200_OK, UrlSchema.from_orm(url)