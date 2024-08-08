import random
import string
import datetime

from functools import wraps
from typing import Optional, List
from pydantic import HttpUrl

from ninja import Router, Schema
from django.shortcuts import get_object_or_404

from .. import api
from ..models import Url

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

# 身分驗證的函式
def check_auth(request, required_type=None):
    if not hasattr(request, 'auth'):
        request.auth = None
    if not request.auth or (required_type is not None and request.auth.user_type != required_type):
        return False
    return True

# 權限檢查裝飾器
def user_auth_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not check_auth(request):
            return api.create_response(request, {"message": "您必須登入才能執行此操作。"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

def admin_auth_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not check_auth(request, required_type=2):
            return api.create_response(request, {"message": "您必須是管理員才能執行此操作。"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

# 使用者是否可以編輯短網址的裝飾器
def user_can_edit_url(func):
    @wraps(func)
    def wrapper(request, short_string, *args, **kwargs):
        if not hasattr(request, 'auth'):
            request.auth = None
        url = Url.objects.filter(short_string=short_string).first()
        if not url:
            return api.create_response(request, {"message": "找不到此短網址。"}, status=404)
        if not request.auth or (url.user != request.auth and request.auth.user_type != 2):
            return api.create_response(request, {"message": "您沒有權限編輯此短網址。"}, status=403)
        return func(request, short_string, *args, **kwargs)
    return wrapper

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
        origin_url = str(origin_url),
        short_string = short_string,
        short_url = str(short_url),
        create_date = datetime.datetime.now(),
        expire_date = expire_date,
        user = user
    )

# POST : 新增短網址 API /api/short-url/short
@url_router.post("short", auth=None, response={201: UrlSchema, 400: ErrorSchema})
def create_short_url(request, origin_url: HttpUrl, expire_date: Optional[datetime.datetime] = None):
    if not hasattr(request, 'auth'):
        request.auth = None
    short_string = generate_short_url()
    short_url = HttpUrl(handle_domain(request, short_string))
    user = request.auth if request.auth else None
    url = create_url_entry(origin_url, short_string, short_url, expire_date, user=user)
    return 201, url

# POST : 新增自訂短網址 API /api/short-url/custom
@url_router.post("custom", response={201: UrlSchema, 400: ErrorSchema})
@user_auth_required
def create_custom_url(request, origin_url: HttpUrl, short_string: str, expire_date: Optional[datetime.datetime] = None):
    short_url = HttpUrl(handle_domain(request, short_string))
    if Url.objects.filter(short_url=str(short_url)).exists():
        return 400, {"message": "自訂短網址已存在，請更換其他短網址。"}
    else:
        url = create_url_entry(origin_url, short_string, short_url, expire_date, user=request.auth)
        return 201, url

# GET : 以縮短網址字符查詢原網址 API /api/short-url/origin/{short_string}
@url_router.get('origin/{short_string}', auth=None, response={200: UrlSchema, 404: ErrorSchema})
def get_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return 200, url

# GET : 查詢自己所有短網址 API /api/short-url/all-my
@url_router.get('all-my', response=List[UrlSchema])
@user_auth_required
def get_all_myurl(request):
    url = Url.objects.filter(user=request.auth)
    return url

# GET : 查詢所有短網址 API /api/short-url/all
@url_router.get('all', response=List[UrlSchema])
@admin_auth_required
def get_all_url(request):
    url = Url.objects.all()
    return url

# DELETE : 刪除短網址 API /api/short-url/url/{short_string}
@url_router.delete('url/{short_string}', response={204: None, 404: ErrorSchema})
@user_can_edit_url
def delete_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    url.delete()
    return 204, None

# DELETE : 刪除過期的短網址 API /api/short-url/expire
@url_router.delete('expire', response={204: None})
@admin_auth_required
def delete_expire_url(request):
    url = Url.objects.filter(expire_date__lt=datetime.datetime.now())
    url.delete()
    return 204, None