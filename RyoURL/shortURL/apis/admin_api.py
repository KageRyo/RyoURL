from ninja import Router
from typing import List
import datetime
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from rest_framework import status

from ..models import Url, User
from .auth import JWTAuth
from .schemas import UrlSchema, ErrorSchema, UserInfoSchema

admin_auth = JWTAuth()

class AdminRouter(Router):
    def get_permissions(self, request):
        auth = admin_auth.authenticate(request, request.headers.get('Authorization', '').split(' ')[-1])
        if not admin_auth.admin_check(auth):
            raise HttpError(status.HTTP_403_FORBIDDEN, "需要管理員權限")
        request.auth = auth

admin_router = AdminRouter(tags=["admin"])

@admin_router.get('all-urls', response={status.HTTP_200_OK: List[UrlSchema], status.HTTP_403_FORBIDDEN: ErrorSchema})
def get_all_url(request):
    admin_router.get_permissions(request)
    urls = Url.objects.all()
    return status.HTTP_200_OK, [UrlSchema.from_orm(url) for url in urls]

@admin_router.delete('expire-urls', response={status.HTTP_204_NO_CONTENT: None, status.HTTP_403_FORBIDDEN: ErrorSchema})
def delete_expire_url(request):
    admin_router.get_permissions(request)
    Url.objects.filter(expire_date__lt=datetime.datetime.now()).delete()
    return status.HTTP_204_NO_CONTENT, None

@admin_router.get('users', response={status.HTTP_200_OK: List[UserInfoSchema], status.HTTP_403_FORBIDDEN: ErrorSchema})
def get_all_users(request):
    admin_router.get_permissions(request)
    users = User.objects.all()
    return status.HTTP_200_OK, [UserInfoSchema(username=user.username, user_type=user.user_type) for user in users]

@admin_router.put('user/{username}', response={status.HTTP_200_OK: UserInfoSchema, status.HTTP_403_FORBIDDEN: ErrorSchema, status.HTTP_404_NOT_FOUND: ErrorSchema})
def update_user_type(request, username: str, user_type: int):
    admin_router.get_permissions(request)
    user = get_object_or_404(User, username=username)
    user.user_type = user_type
    user.save()
    return status.HTTP_200_OK, UserInfoSchema(username=user.username, user_type=user.user_type)

@admin_router.delete('user/{username}', response={status.HTTP_204_NO_CONTENT: None, status.HTTP_403_FORBIDDEN: ErrorSchema, status.HTTP_404_NOT_FOUND: ErrorSchema})
def delete_user(request, username: str):
    admin_router.get_permissions(request)
    user = get_object_or_404(User, username=username)
    user.delete()
    return status.HTTP_204_NO_CONTENT, None