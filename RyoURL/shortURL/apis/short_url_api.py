import random
import string
import datetime
from typing import List
from ninja import Router
from django.shortcuts import get_object_or_404

from ..models import Url
from .auth_api import JWTAuth
from .schemas import UrlSchema, ErrorSchema, UrlCreateSchema, CustomUrlCreateSchema

url_router = Router(tags=["short-url"])

def generate_short_url(length=6):
    char = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(char, k=length))
        if not Url.objects.filter(short_string=short_url).exists():
            return short_url

def handle_domain(request, short_string):
    domain = request.build_absolute_uri('/')[:-1].strip('/')
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

@url_router.post("short", auth=None, response={201: UrlSchema, 400: ErrorSchema})
def create_short_url(request, data: UrlCreateSchema):
    short_string = generate_short_url()
    short_url = handle_domain(request, short_string)
    
    user = getattr(request, 'auth', {}).get('user') if hasattr(request, 'auth') else None
    
    try:
        url = create_url_entry(data.origin_url, short_string, short_url, data.expire_date, user=user)
        return 201, url
    except Exception as e:
        return 400, {"message": str(e)}

@url_router.post("custom", auth=JWTAuth(), response={201: UrlSchema, 400: ErrorSchema, 403: ErrorSchema})
def create_custom_url(request, data: CustomUrlCreateSchema):
    if request.auth['user_type'] < 1:
        return 403, {"message": "無權限使用此功能"}

    short_url = handle_domain(request, data.short_string)
    if Url.objects.filter(short_string=data.short_string).exists():
        return 400, {"message": "自訂短網址已存在，請更換其他短網址。"}
    
    try:
        url = create_url_entry(data.origin_url, data.short_string, short_url, data.expire_date, user=request.auth['user'])
        return 201, url
    except Exception as e:
        return 400, {"message": str(e)}

@url_router.get('origin/{short_string}', auth=None, response={200: UrlSchema, 404: ErrorSchema})
def get_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return 200, url

@url_router.get('all-my', auth=JWTAuth(), response={200: List[UrlSchema], 403: ErrorSchema})
def get_all_myurl(request):
    if request.auth['user_type'] < 1:
        return 403, {"message": "無權限使用此功能"}
    urls = Url.objects.filter(user=request.auth['user'])
    return 200, urls

@url_router.delete('url/{short_string}', auth=JWTAuth(), response={204: None, 404: ErrorSchema, 403: ErrorSchema})
def delete_short_url(request, short_string: str):
    if request.auth['user_type'] < 1:
        return 403, {"message": "無權限使用此功能"}
    url = get_object_or_404(Url, short_string=short_string)
    if url.user != request.auth['user']:
        return 403, {"message": "無權限刪除此短網址"}
    url.delete()
    return 204, None