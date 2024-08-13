from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .schemas import UserResponseSchema, ErrorSchema, TokenSchema, TokenResponseSchema
from ..models import User
from .auth_api import JWTAuth

user_router = Router(tags=["user"])

@user_router.get("info", auth=JWTAuth(), response={200: UserResponseSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_user_info(request, username: str):
    if not request.auth:
        return 403, {"message": "需要登入"}
    
    if username == request.auth['user'].username or request.auth['user_type'] == 2:
        try:
            user = User.objects.get(username=username)
            return 200, {"username": user.username, "user_type": user.user_type}
        except User.DoesNotExist:
            return 404, {"message": "使用者不存在"}
    else:
        return 403, {"message": "無權限查看其他使用者資訊"}

@user_router.post("refresh-token", auth=JWTAuth(), response={200: TokenResponseSchema, 400: ErrorSchema})
def refresh_token(request, token_data: TokenSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return 200, {"access": str(refresh.access_token)}
    except TokenError:
        return 400, {"message": "無效的更新權杖"}