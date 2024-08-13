from django.contrib.auth import authenticate
from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken

from .schemas import UserSchema, UserResponseSchema, ErrorSchema
from ..models import User
from .auth import JWTAuth

auth_router = Router(tags=["auth"])

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
            "user_type": user.user_type,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    except Exception as e:
        return 400, {"message": f"註冊失敗: {str(e)}"}
    
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
            "user_type": user.user_type,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }    
    else:
        return 400, {"message": "登入失敗"}