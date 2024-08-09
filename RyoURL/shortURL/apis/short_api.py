import random
import string
import datetime
from typing import Optional, List
from pydantic import HttpUrl
from ninja import Router, Schema
from django.shortcuts import get_object_or_404

from ..models import Url
from .auth_api import JWTAuth

url_router = Router(tags=["short-url"])

# 定義 Url 的 Schema 類別
class UrlSchema(Schema):
    origin_url: HttpUrl
    short_string: str
    short_url: HttpUrl
    create_date: datetime.datetime
    expire_date: Optional[datetime.datetime]
    visit_count: int

# 定義錯誤回應的 Schema 類別
class ErrorSchema(Schema):
    message: str

# 產生隨機短網址的函式
def generate_short_url(length = 6):
    char = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(char, k=length))
        if not Url.objects.filter(short_url=short_url).exists():
            return short_url

# 處理短網址域名的函式
def handle_domain(request, short_string):
    domain = request.build_absolute_uri('/')[:-1].strip('/')
    return f'{domain}/{short_string}'

# 建立短網址物件的函式
def create_url_entry(origin_url: HttpUrl, short_string: str, short_url: HttpUrl, expire_date: Optional[datetime.datetime] = None, user=None) -> Url:
    return Url.objects.create(
        origin_url=str(origin_url),
        short_string=short_string,
        short_url=str(short_url),
        create_date=datetime.datetime.now(),
        expire_date=expire_date,
        user=user
    )

# 檢查用戶權限的函式
def check_user_permission(request, required_user_type: int):
    if not hasattr(request, 'auth') or request.auth['user_type'] != required_user_type:
        return False, {"message": "無權限訪問"}
    return True, None

# POST : 新增隨機短網址 API /api/short-url/short
@url_router.post("short", auth=None, response={201: UrlSchema, 400: ErrorSchema})
def create_short_url(request, origin_url: HttpUrl, expire_date: Optional[datetime.datetime] = None):
    short_string = generate_short_url()
    short_url = HttpUrl(handle_domain(request, short_string))
    
    user = getattr(request, 'auth', {}).get('user') if hasattr(request, 'auth') else None
    
    url = create_url_entry(origin_url, short_string, short_url, expire_date, user=user)
    return 201, url

# POST : 新增自訂短網址 API /api/short-url/custom
@url_router.post("custom", auth=JWTAuth(), response={201: UrlSchema, 400: ErrorSchema, 403: ErrorSchema})
def create_custom_url(request, origin_url: HttpUrl, short_string: str, expire_date: Optional[datetime.datetime] = None):
    has_permission, error_response = check_user_permission(request, required_user_type=1)
    if not has_permission:
        return 403, error_response

    short_url = HttpUrl(handle_domain(request, short_string))
    if Url.objects.filter(short_url=str(short_url)).exists():
        return 400, {"message": "自訂短網址已存在，請更換其他短網址。"}
    else:
        url = create_url_entry(origin_url, short_string, short_url, expire_date, user=request.auth['user'])
        return 201, url

# GET : 以短網址字符查詢原網址 API /api/short-url/origin/{short_string}
@url_router.get('origin/{short_string}', auth=None, response={200: UrlSchema, 404: ErrorSchema})
def get_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return 200, url

# GET : 查詢自己所有短網址 API /api/short-url/all-my
@url_router.get('all-my', auth=JWTAuth(), response={200: List[UrlSchema], 403: ErrorSchema})
def get_all_myurl(request):
    has_permission, error_response = check_user_permission(request, required_user_type=1)
    if not has_permission:
        return 403, error_response

    url = Url.objects.filter(user=request.auth['user'])
    return url

# GET : 查詢所有短網址 API /api/short-url/all
@url_router.get('all', auth=JWTAuth(), response={200: List[UrlSchema], 403: ErrorSchema})
def get_all_url(request):
    has_permission, error_response = check_user_permission(request, required_user_type=2)
    if not has_permission:
        return 403, error_response

    url = Url.objects.all()
    return url

# DELETE : 刪除短網址 API /api/short-url/url/{short_string}
@url_router.delete('url/{short_string}', auth=JWTAuth(), response={204: None, 404: ErrorSchema, 403: ErrorSchema})
def delete_short_url(request, short_string: str):
    has_permission, error_response = check_user_permission(request, required_user_type=1)
    if not has_permission:
        return 403, error_response

    url = get_object_or_404(Url, short_string=short_string)
    if url.user != request.auth['user']:
        return 403, {"message": "無權限刪除此短網址"}
    url.delete()
    return 204, None

# DELETE : 刪除過期的短網址 API /api/short-url/expire
@url_router.delete('expire', auth=JWTAuth(), response={204: None, 403: ErrorSchema})
def delete_expire_url(request):
    has_permission, error_response = check_user_permission(request, required_user_type=2)
    if not has_permission:
        return 403, error_response

    url = Url.objects.filter(expire_date__lt=datetime.datetime.now())
    url.delete()
    return 204, None