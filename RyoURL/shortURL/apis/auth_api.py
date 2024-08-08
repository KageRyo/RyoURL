from ninja import Router, Schema
from ninja.security import HttpBearer
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from ..models import User

auth_router = Router(tags=["auth"])

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

# 定義錯誤回應的 Schema 類別
class ErrorSchema(Schema):
    message: str

# JWT 認證類別
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            request.auth = user
            return user
        except:
            request.auth = None
            return None

# POST : 註冊 API /api/auth/register
@auth_router.post("register", auth=None, response={201: UserResponseSchema, 400: ErrorSchema})
def register_user(request, user_data: UserSchema):
    try:
        user = User.objects.create_user(
            username=user_data.username, 
            password=user_data.password
        )
        refresh = RefreshToken.for_user(user)
        return 201, {
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    except:
        return 400, {"message": "註冊失敗"}
    
# POST : 登入 API /api/auth/login
@auth_router.post("login", auth=None, response={200: UserResponseSchema, 400: ErrorSchema})
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

# POST : 更新 TOKEN API /api/auth/refresh-token
@auth_router.post("refresh-token", auth=None, response={200: TokenResponseSchema, 400: ErrorSchema})
def refresh_token(request, token_data: TokenSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return 200, {"access": str(refresh.access_token)}
    except TokenError:
        return 400, {"message": "無效的更新權杖"}