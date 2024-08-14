from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from ninja.errors import HttpError
from rest_framework import status

from .schemas import UserInfoSchema, ErrorSchema, TokenSchema, TokenResponseSchema
from ..models import User
from .auth import JWTAuth

user_auth = JWTAuth()

class UserRouter(Router):
    def get_permissions(self, request):
        auth = user_auth.authenticate(request, request.headers.get('Authorization', '').split(' ')[-1])
        if not user_auth.user_check(auth):
            raise HttpError(status.HTTP_403_FORBIDDEN, "需要登入")
        request.auth = auth

user_router = UserRouter(tags=["user"])

@user_router.get("info", response={status.HTTP_200_OK: UserInfoSchema, status.HTTP_403_FORBIDDEN: ErrorSchema, status.HTTP_404_NOT_FOUND: ErrorSchema})
def get_user_info(request, username: str):
    if username != request.auth['user'].username and not user_auth.admin_check(request.auth):
        raise HttpError(status.HTTP_403_FORBIDDEN, "無權限查看其他使用者資訊")
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise HttpError(status.HTTP_404_NOT_FOUND, "使用者不存在")
    
    return status.HTTP_200_OK, UserInfoSchema(username=user.username, user_type=user.user_type)

@user_router.post("refresh-token", response={status.HTTP_200_OK: TokenResponseSchema, status.HTTP_400_BAD_REQUEST: ErrorSchema})
def refresh_token(request, token_data: TokenSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return status.HTTP_200_OK, TokenResponseSchema(access=str(refresh.access_token))
    except TokenError:
        raise HttpError(status.HTTP_400_BAD_REQUEST, "無效的更新權杖")