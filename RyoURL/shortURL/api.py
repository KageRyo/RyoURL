import random
import string
import datetime

from functools import wraps
from typing import List, Optional
from pydantic import HttpUrl, AnyUrl

from ninja import NinjaAPI, Schema
from ninja.security import HttpBearer
from ninja.renderers import JSONRenderer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate

from .models import Url, User

# 自定義 JSON 編碼器類別
class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, AnyUrl): 
            return str(obj)
        return super().default(obj)

# 自定義 JSON 渲染器類別
class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder
    
# JWT 認證類別
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            request.auth = user  # 將使用者設置到 request.auth
            return user
        except:
            request.auth = None  # 確保 request.auth 始終存在
            return None

# 初始化 API，並使用自定義的 JSON 渲染器和 JWT 認證
api = NinjaAPI(renderer=CustomJSONRenderer(), auth=JWTAuth())

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

# 定義 User 的 Schema 類別
class UserSchema(Schema):
    username: str
    password: str
    
# 定義 Token 的 Schema 類別
class TokenSchema(Schema):
    refresh: str

# 定義 Token 回應的 Schema 類別
class TokenResponseSchema(Schema):
    access: str
    
# 定義 User 註冊或登入回應的 Schema 類別
class UserResponseSchema(Schema):
    username: str
    access: str
    refresh: str

# 權限檢查裝飾器
def user_auth_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'auth'):
            request.auth = None
        if not request.auth:
            return api.create_response(request, {"message": "您必須登入才能執行此操作。"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

def admin_auth_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'auth'):
            request.auth = None
        if not request.auth or request.auth.user_type != 2:
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
def generator_short_url(length = 6):
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
@api.get("/", auth=None, response={200: ErrorSchema})
def index(request):
    return 200, {"message": "已與 RyoURL 建立連線。"}

# POST : 註冊 API /register
@api.post("register", auth=None, response={200: UserResponseSchema, 400: ErrorSchema})
def register_user(request, user_data: UserSchema):
    try:
        user = User.objects.create_user(
            username=user_data.username, 
            password=user_data.password
        )
        refresh = RefreshToken.for_user(user)
        return 200, {
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    except:
        return 400, {"message": "註冊失敗"}
    
# POST : 登入 API /login
@api.post("login", auth=None, response={200: UserResponseSchema, 400: ErrorSchema})
def login_user(request, user_data: UserSchema):
    user = authenticate(
        username=user_data.username, 
        password=user_data.password
    )
    if user:
        refresh = RefreshToken.for_user(user)
        return 200, {
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }    
    else:
        return 400, {"message": "登入失敗"}

# POST : 更新 TOKEN API /refresh-token
@api.post("refresh-token", auth=None, response={200: TokenResponseSchema, 400: ErrorSchema})
def refresh_token(request, token_data: TokenSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return 200, {"access": str(refresh.access_token)}
    except TokenError:
        return 400, {"message": "無效的更新權杖"}

# POST : 新增短網址 API /short-url
@api.post("short-url", auth=None, response={200: UrlSchema, 404: ErrorSchema})
def create_short_url(request, orign_url: HttpUrl, expire_date: Optional[datetime.datetime] = None):
    if not hasattr(request, 'auth'):
        request.auth = None
    short_string = generator_short_url()
    short_url = HttpUrl(handle_domain(request, short_string))
    user = request.auth if request.auth else None
    url = create_url_entry(orign_url, short_string, short_url, expire_date, user=user)
    return 200, url

# POST : 新增自訂短網址 API /custom-url
@api.post("custom-url", response={200: UrlSchema, 403: ErrorSchema})
@user_auth_required
def create_custom_url(request, orign_url: HttpUrl, short_string: str, expire_date: Optional[datetime.datetime] = None):
    short_url = HttpUrl(handle_domain(request, short_string))
    if Url.objects.filter(short_url=str(short_url)).exists():
        return 403, {"message": "自訂短網址已存在，請更換其他短網址。"}
    else:
        url = create_url_entry(orign_url, short_string, short_url, expire_date, user=request.auth)
        return 200, url

# GET : 以縮短網址字符查詢原網址 API /orign-url/{short_string}
@api.get('orign-url/{short_string}', auth=None, response={200: UrlSchema})
def get_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    return 200, url

# GET : 查詢自己所有短網址 API /all-myurl
@api.get('all-myurl', response=List[UrlSchema])
@user_auth_required
def get_all_myurl(request):
    url = Url.objects.filter(user=request.auth)
    return url

# GET : 查詢所有短網址 API /all-url
@api.get('all-url', response=List[UrlSchema])
@admin_auth_required
def get_all_url(request):
    url = Url.objects.all()
    return url

# DELETE : 刪除短網址 API /short-url/{short_string}
@api.delete('short-url/{short_string}', response={200: ErrorSchema})
@user_can_edit_url
def delete_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    url.delete()
    return 200, {"message": "成功刪除！"}

# DELETE : 刪除過期短網址 API /expire-url
@api.delete('expire-url', response={200: ErrorSchema})
@admin_auth_required
def delete_expire_url(request):
    url = Url.objects.filter(expire_date__lt=datetime.datetime.now())
    url.delete()
    return 200, {"message": "成功刪除過期的短網址！"}