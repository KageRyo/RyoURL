from ninja import Router
from typing import List
import datetime
from django.shortcuts import get_object_or_404

from ..models import Url, User
from .auth_api import JWTAuth
from .schemas import UrlSchema, ErrorSchema, UserSchema, UserResponseSchema

admin_router = Router(tags=["admin"])

@admin_router.get('all-urls', auth=JWTAuth(), response={200: List[UrlSchema], 403: ErrorSchema})
def get_all_url(request):
    if request.auth['user_type'] != 2:
        return 403, {"message": "需要管理員權限"}
    urls = Url.objects.all()
    return 200, urls

@admin_router.delete('expire-urls', auth=JWTAuth(), response={204: None, 403: ErrorSchema})
def delete_expire_url(request):
    if request.auth['user_type'] != 2:
        return 403, {"message": "需要管理員權限"}
    Url.objects.filter(expire_date__lt=datetime.datetime.now()).delete()
    return 204, None

@admin_router.get('users', auth=JWTAuth(), response={200: List[UserResponseSchema], 403: ErrorSchema})
def get_all_users(request):
    if request.auth['user_type'] != 2:
        return 403, {"message": "需要管理員權限"}
    users = User.objects.all()
    return 200, [{"username": user.username, "user_type": user.user_type} for user in users]

@admin_router.put('user/{username}', auth=JWTAuth(), response={200: UserResponseSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_user_type(request, username: str, user_type: int):
    if request.auth['user_type'] != 2:
        return 403, {"message": "需要管理員權限"}
    user = get_object_or_404(User, username=username)
    user.user_type = user_type
    user.save()
    return 200, {"username": user.username, "user_type": user.user_type}

@admin_router.delete('user/{username}', auth=JWTAuth(), response={204: None, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, username: str):
    if request.auth['user_type'] != 2:
        return 403, {"message": "需要管理員權限"}
    user = get_object_or_404(User, username=username)
    user.delete()
    return 204, None