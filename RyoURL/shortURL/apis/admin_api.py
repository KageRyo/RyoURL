from ninja import Router
from typing import List
import datetime
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from ..models import Url, User
from .auth import JWTAuth
from .schemas import UrlSchema, ErrorSchema, UserResponseSchema

admin_auth = JWTAuth()

class AdminRouter(Router):
    def get_permissions(self, request):
        auth = admin_auth.authenticate(request, request.headers.get('Authorization', '').split(' ')[-1])
        if not admin_auth.admin_check(auth):
            raise HttpError(403, "需要管理員權限")

admin_router = AdminRouter(tags=["admin"])

@admin_router.get('all-urls', response={200: List[UrlSchema], 403: ErrorSchema})
def get_all_url(request):
    urls = Url.objects.all()
    return 200, urls

@admin_router.delete('expire-urls', response={204: None, 403: ErrorSchema})
def delete_expire_url(request):
    Url.objects.filter(expire_date__lt=datetime.datetime.now()).delete()
    return 204, None

@admin_router.get('users', response={200: List[UserResponseSchema], 403: ErrorSchema})
def get_all_users(request):
    users = User.objects.all()
    return 200, [{"username": user.username, "user_type": user.user_type} for user in users]

@admin_router.put('user/{username}', response={200: UserResponseSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_user_type(request, username: str, user_type: int):
    user = get_object_or_404(User, username=username)
    user.user_type = user_type
    user.save()
    return 200, {"username": user.username, "user_type": user.user_type}

@admin_router.delete('user/{username}', response={204: None, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, username: str):
    user = get_object_or_404(User, username=username)
    user.delete()
    return 204, None