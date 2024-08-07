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

from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout

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
    
# JWT 認證類別
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            return user
        except:
            return None

# 初始化 API，並使用自定義的 JSON 渲染器及 JWT 認證
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
    
# 定義 User 註冊或登入回應的 Schema 類別
class UserResponseSchema(Schema):
    username: str

# 一般使用者的權限檢查裝飾器
def user_is_authenticated(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return api.create_response(request, {"message": "您必須登錄才能執行此操作。"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

# 管理員的權限檢查裝飾器
def user_is_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 2:
            return api.create_response(request, {"message": "您必須是管理員才能執行此操作。"}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

# 使用者是否可以編輯短網址的裝飾器
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

# 產生隨機短網址的函式
def generator_short_url(length = 6):
    char = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(char, k=length))
        if not Url.objects.filter(short_url=short_url).exists():
            return short_url   # 如果短網址不存在 DB 中，則回傳此短網址
    
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

# POST : 註冊 API /register
@api.post("register", response={200: UserResponseSchema, 400: ErrorSchema})
def register_user(request, user_data: UserSchema):
    try:
        user = User.objects.create_user(
            username=user_data.username, 
            password=user_data.password
        )
        return 200, {"username": user.username}
    except:
        return 400, {"message": "註冊失敗"}
    
# POST : 登入 API /login
@api.post("login", response={200: UserResponseSchema, 400: ErrorSchema})
def login_user(request, user_data: UserSchema):
    user = authenticate(
        username=user_data.username, 
        password=user_data.password
    )
    if user:
        login(request, user)
        return 200, {"username": user.username}
    else:
        return 400, {"message": "登入失敗"}
    
# POST : 登出 API /logout
@api.post("logout", response={200: ErrorSchema})
@user_is_authenticated
def logout_user(request):
    logout(request)
    return 200, {"message": "登出成功"}

# POST : 新增短網址 API /short_url
@api.post("short-url", response={200: UrlSchema, 404: ErrorSchema})
def create_short_url(request, orign_url: HttpUrl, expire_date: Optional[datetime.datetime] = None):
    short_string = generator_short_url()
    short_url = HttpUrl(handle_domain(request, short_string))
    user = request.user if request.user.is_authenticated else None
    url = create_url_entry(orign_url, short_string, short_url, expire_date, user=user)
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

# GET : 查詢自己所有短網址 API /all_myurl
@api.get('all-myurl', response=List[UrlSchema])
@user_is_authenticated
def get_all_myurl(request):
    url = Url.objects.filter(user=request.user)
    return url

# GET : 查詢所有短網址 API /all_url
@api.get('all-url', response=List[UrlSchema])
@user_is_admin
def get_all_url(request):
    url = Url.objects.all()
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