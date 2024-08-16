from http import HTTPStatus
from django.contrib.auth import authenticate
from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken
from ninja.errors import HttpError
from django.db import IntegrityError

from .schemas import UserSchema, UserResponseSchema, ErrorSchema
from ..models import User
from .auth import JWTAuth

auth_router = Router(tags=["auth"])

@auth_router.post("register", auth=None, response={HTTPStatus.CREATED: UserResponseSchema, HTTPStatus.BAD_REQUEST: ErrorSchema})
def register_user(request, user_data: UserSchema):
    try:
        user = User.objects.create_user(
            username=user_data.username, 
            password=user_data.password
        )
    except IntegrityError:
        raise HttpError(HTTPStatus.BAD_REQUEST, "用戶名已存在")
    except Exception as e:
        raise HttpError(HTTPStatus.BAD_REQUEST, f"註冊失敗: {str(e)}")
    
    refresh = RefreshToken.for_user(user)
    return HTTPStatus.CREATED, UserResponseSchema(
        username=user.username,
        user_type=user.user_type,
        access=str(refresh.access_token),
        refresh=str(refresh)
    )
    
@auth_router.post("login", auth=None, response={HTTPStatus.OK: UserResponseSchema, HTTPStatus.BAD_REQUEST: ErrorSchema})
def login_user(request, user_data: UserSchema):
    user = authenticate(
        username=user_data.username, 
        password=user_data.password
    )
    if not user:
        raise HttpError(HTTPStatus.BAD_REQUEST, "登入失敗")
    
    refresh = RefreshToken.for_user(user)
    return HTTPStatus.OK, UserResponseSchema(
        username=user.username,
        user_type=user.user_type,
        access=str(refresh.access_token),
        refresh=str(refresh)
    )