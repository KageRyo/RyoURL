import random
import string
import datetime
from ninja import Router
from django.shortcuts import get_object_or_404
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

@short_url_router.post("/short", response={201: UrlSchema, 400: ErrorSchema})
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
        return 201, UrlSchema(
            origin_url=url.origin_url,
            short_string=url.short_string,
            short_url=url.short_url,
            create_date=url.create_date,
            expire_date=url.expire_date,
            visit_count=url.visit_count,
            creator_username=url.user.username if url.user.username != 'anonymous' else None
        )
    except Exception as e:
        return 400, {"message": str(e)}

@short_url_router.get("/origin/{short_string}", response={200: UrlSchema, 404: ErrorSchema})
def get_original_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return UrlSchema.from_orm(url)