from http import HTTPStatus
from ninja import Router
from typing import List
import datetime
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from ..models import Url, User
from .schemas import UrlSchema, ErrorSchema, UserInfoSchema

admin_router = Router()

@admin_router.get('all-urls', response={HTTPStatus.OK: List[UrlSchema], HTTPStatus.FORBIDDEN: ErrorSchema})
def get_all_url(request):
    urls = Url.objects.all()
    return HTTPStatus.OK, [UrlSchema.from_orm(url) for url in urls]

@admin_router.delete('expire-urls', response={HTTPStatus.NO_CONTENT: None, HTTPStatus.FORBIDDEN: ErrorSchema})
def delete_expire_url(request):
    Url.objects.filter(expire_date__lt=datetime.datetime.now()).delete()
    return HTTPStatus.NO_CONTENT, None

@admin_router.get('users', response={HTTPStatus.OK: List[UserInfoSchema], HTTPStatus.FORBIDDEN: ErrorSchema})
def get_all_users(request):
    users = User.objects.all()
    return HTTPStatus.OK, [UserInfoSchema(username=user.username, user_type=user.user_type) for user in users]

@admin_router.put('user/{username}', response={HTTPStatus.OK: UserInfoSchema, HTTPStatus.FORBIDDEN: ErrorSchema, HTTPStatus.NOT_FOUND: ErrorSchema})
def update_user_type(request, username: str, user_type: int):
    user = get_object_or_404(User, username=username)
    user.user_type = user_type
    user.save()
    return HTTPStatus.OK, UserInfoSchema(username=user.username, user_type=user.user_type)

@admin_router.delete('user/{username}', response={HTTPStatus.NO_CONTENT: None, HTTPStatus.FORBIDDEN: ErrorSchema, HTTPStatus.NOT_FOUND: ErrorSchema})
def delete_user(request, username: str):
    user = get_object_or_404(User, username=username)
    user.delete()
    return HTTPStatus.NO_CONTENT, None