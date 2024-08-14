from django.contrib.auth import authenticate
from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .schemas import UserSchema, UserResponseSchema, ErrorSchema
from ..models import User
from .auth import JWTAuth

auth_router = Router(tags=["auth"])

@auth_router.post("register", auth=None, response={status.HTTP_201_CREATED: UserResponseSchema, status.HTTP_400_BAD_REQUEST: ErrorSchema})
def register_user(request, user_data: UserSchema):
    try:
        user = User.objects.create_user(
            username=user_data.username, 
            password=user_data.password
        )
        refresh = RefreshToken.for_user(user)
        return status.HTTP_201_CREATED, UserResponseSchema(
            username=user.username,
            user_type=user.user_type,
            access=str(refresh.access_token),
            refresh=str(refresh)
        )
    except Exception as e:
        return status.HTTP_400_BAD_REQUEST, ErrorSchema(message=f"註冊失敗: {str(e)}")
    
@auth_router.post("login", auth=None, response={status.HTTP_200_OK: UserResponseSchema, status.HTTP_400_BAD_REQUEST: ErrorSchema})
def login_user(request, user_data: UserSchema):
    user = authenticate(
        username=user_data.username, 
        password=user_data.password
    )
    if user:
        refresh = RefreshToken.for_user(user)
        return status.HTTP_200_OK, UserResponseSchema(
            username=user.username,
            user_type=user.user_type,
            access=str(refresh.access_token),
            refresh=str(refresh)
        )
    else:
        return status.HTTP_400_BAD_REQUEST, ErrorSchema(message="登入失敗")