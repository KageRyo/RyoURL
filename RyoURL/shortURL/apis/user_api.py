from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from ninja.errors import HttpError
from rest_framework import status

from .schemas import UserResponseSchema, ErrorSchema, TokenSchema, TokenResponseSchema
from ..models import User
from .auth import JWTAuth

user_auth = JWTAuth()

class UserRouter(Router):
    def get_permissions(self, request):
        if not user_auth.user_check(user_auth.authenticate(request, request.headers.get('Authorization', '').split(' ')[-1])):
            raise HttpError(status.HTTP_403_FORBIDDEN, "需要登入")

user_router = UserRouter(tags=["user"])

@user_router.get("info", response={status.HTTP_200_OK: UserResponseSchema, status.HTTP_403_FORBIDDEN: ErrorSchema, status.HTTP_404_NOT_FOUND: ErrorSchema})
def get_user_info(request, username: str):
    if username == request.auth['user'].username or user_auth.admin_check(request.auth):
        try:
            user = User.objects.get(username=username)
            return status.HTTP_200_OK, UserResponseSchema(username=user.username, user_type=user.user_type)
        except User.DoesNotExist:
            return status.HTTP_404_NOT_FOUND, ErrorSchema(message="使用者不存在")
    else:
        return status.HTTP_403_FORBIDDEN, ErrorSchema(message="無權限查看其他使用者資訊")

@user_router.post("refresh-token", response={status.HTTP_200_OK: TokenResponseSchema, status.HTTP_400_BAD_REQUEST: ErrorSchema})
def refresh_token(request, token_data: TokenSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return status.HTTP_200_OK, TokenResponseSchema(access=str(refresh.access_token))
    except TokenError:
        return status.HTTP_400_BAD_REQUEST, ErrorSchema(message="無效的更新權杖")