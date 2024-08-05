import random
import string
import datetime

from typing import List, Optional
from pydantic import HttpUrl, AnyUrl

from ninja import NinjaAPI, Schema
from ninja.renderers import JSONRenderer
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseForbidden
from functools import wraps

from .models import Url, User

# 自定義 JSON 編碼器類別
class CustomJSONEncoder(DjangoJSONEncoder):
    # 使用 DjangoJSONEncoder 的 default 方法，並判斷是否為 URL 字串 
    def default(self, obj):
        if isinstance(obj, AnyUrl): 
            return str(obj)         # 強制轉換為字串
        return super().default(obj) # 如果不是 URL 字串，則使用 DjangoJSONEncoder 的 default 方法

# 自定義 JSON 渲染器類別
class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder

# 初始化 API，並使用自定義的 JSON 渲染器
api = NinjaAPI(renderer=CustomJSONRenderer())

# 定義 Url 的 Schema 類別
class UrlSchema(Schema):
    orign_url: HttpUrl
    short_string: str
    short_url: HttpUrl
    create_date: datetime.datetime
    expire_date: Optional[datetime.datetime]
    visit_count: int

# 定義錯誤回應的 Schema 類別
class ErrorSchema(Schema):
    message: str

# 權限檢查裝飾器
def user_is_authenticated(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return api.create_response(request, {"message": "您必須登錄才能執行此操作。"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

def user_is_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 2:
            return api.create_response(request, {"message": "您必須是管理員才能執行此操作。"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

def user_can_edit_url(func):
    @wraps(func)
    def wrapper(request, short_string, *args, **kwargs):
        url = Url.objects.filter(short_string=short_string).first()
        if not url:
            return api.create_response(request, {"message": "找不到此短網址。"}, status=404)
        if url.user != request.user and request.user.user_type != 2:
            return api.create_response(request, {"message": "您沒有權限編輯此短網址。"}, status=403)
        return func(request, short_string, *args, **kwargs)
    return wrapper

# BASE62 編碼的函式
def base62_encode(num):
    base62 = string.digits + string.ascii_letters
    if num == 0:
        return base62[0]
    array = []
    while num:
        num, rem = divmod(num, 62)
        array.append(base62[rem])
    array.reverse()
    return ''.join(array)

# 產生隨機短網址的函式
def generator_short_url(orign_url: str, length = 6):
    hash_value = abs(hash(orign_url))   # 取得原網址的 hash 值
    encode = base62_encode(hash_value)  # 將 hash 值轉換為 BASE62 編碼
    if len(encode) < length:
        encode += get_random_string(length - len(encode), string.ascii_letters + string.digits)
        return encode
    return encode[:length]
    
# 處理短網址域名的函式
def handle_domain(request, short_string):
    domain = request.build_absolute_uri('/')[:-1].strip('/')
    return f'{domain}/{short_string}'

# 建立短網址物件的函式
def create_url_entry(orign_url: HttpUrl, short_string: str, short_url: HttpUrl, expire_date: Optional[datetime.datetime] = None, user=None) -> Url:
    return Url.objects.create(
        orign_url = str(orign_url),
        short_string = short_string,
        short_url = str(short_url),
        create_date = datetime.datetime.now(),
        expire_date = expire_date,
        user = user
    )

# GET : 首頁 API /
@api.get("/", response={200: ErrorSchema})
def index(request):
    return 200, {"message": "已與 RyoURL 建立連線。"}

# POST : 新增短網址 API /short_url
@api.post("short-url", response={200: UrlSchema, 404: ErrorSchema})
@user_is_authenticated
def create_short_url(request, orign_url: HttpUrl, expire_date: Optional[datetime.datetime] = None):
    short_string = generator_short_url(orign_url)
    short_url = HttpUrl(handle_domain(request, short_string))
    url = create_url_entry(orign_url, short_string, short_url, expire_date, user=request.user)
    return 200, url

# POST : 新增自訂短網址 API /custom_url
@api.post("custom-url", response={200: UrlSchema, 403: ErrorSchema})
@user_is_authenticated
def create_custom_url(request, orign_url: HttpUrl, short_string: str, expire_date: Optional[datetime.datetime] = None):
    short_url = HttpUrl(handle_domain(request, short_string))
    if Url.objects.filter(short_url=str(short_url)).exists():
        return 403, {"message": "自訂短網址已存在，請更換其他短網址。"}
    else:
        url = create_url_entry(orign_url, short_string, short_url, expire_date, user=request.user)
        return 200, url

# GET : 以縮短網址字符查詢原網址 API /orign_url/{short_string}
@api.get('orign-url/{short_string}', response={200: UrlSchema})
def get_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return 200, url

# GET : 查詢所有短網址 API /all_url
@api.get('all-url', response=List[UrlSchema])
@user_is_authenticated
def get_all_url(request):
    url = Url.objects.filter(user=request.user)
    return url
 
# DELETE : 刪除短網址 API /short_url/{short_string}
@api.delete('short-url/{short_string}', response={200: ErrorSchema})
@user_is_authenticated
@user_can_edit_url
def delete_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    url.delete()
    return 200, {"message": "成功刪除！"}

# DELETE : 刪除過期短網址 API /expire_url
@api.delete('expire-url', response={200: ErrorSchema})
@user_is_admin
def delete_expire_url(request):
    url = Url.objects.filter(expire_date__lt=datetime.datetime.now())
    url.delete()
    return 200, {"message": "成功刪除過期的短網址！"}