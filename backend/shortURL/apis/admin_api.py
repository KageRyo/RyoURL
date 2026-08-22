from http import HTTPStatus
from django.http import Http404
from ninja import Router
from typing import List
import datetime
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from ..models import Url, User
from schemas.schemas import UrlSchema, ErrorSchema, UserInfoSchema

admin_router = Router()

@admin_router.get('all-urls', response={HTTPStatus.OK: List[UrlSchema], HTTPStatus.FORBIDDEN: ErrorSchema})
def get_all_url(request):
    try:
        urls = Url.objects.all()
        return HTTPStatus.OK, [UrlSchema.from_orm(url) for url in urls]
    except Exception as e:
        return HTTPStatus.FORBIDDEN, ErrorSchema(detail=str(e))

@admin_router.delete('expire-urls', response={HTTPStatus.NO_CONTENT: None, HTTPStatus.FORBIDDEN: ErrorSchema})
def delete_expire_url(request):
    try:
        Url.objects.filter(expire_date__lt=datetime.datetime.now()).delete()
        return HTTPStatus.NO_CONTENT, None
    except Exception as e:
        return HTTPStatus.FORBIDDEN, ErrorSchema(detail=str(e))

@admin_router.get('users', response={HTTPStatus.OK: List[UserInfoSchema], HTTPStatus.FORBIDDEN: ErrorSchema})
def get_all_users(request):
    try:
        users = User.objects.all()
        return HTTPStatus.OK, [UserInfoSchema(username=user.username, user_type=user.user_type) for user in users]
    except Exception as e:
        return HTTPStatus.FORBIDDEN, ErrorSchema(detail=str(e))

@admin_router.put('user/{username}', response={HTTPStatus.OK: UserInfoSchema, HTTPStatus.FORBIDDEN: ErrorSchema, HTTPStatus.NOT_FOUND: ErrorSchema})
def update_user_type(request, username: str, user_type: int):
    try:
        user = get_object_or_404(User, username=username)
        user.user_type = user_type
        user.save()
        return HTTPStatus.OK, UserInfoSchema(username=user.username, user_type=user.user_type)
    except Http404:
        return HTTPStatus.NOT_FOUND, ErrorSchema(detail="User not found")
    except Exception as e:
        return HTTPStatus.FORBIDDEN, ErrorSchema(detail=str(e))

@admin_router.delete('user/{username}', response={HTTPStatus.NO_CONTENT: None, HTTPStatus.FORBIDDEN: ErrorSchema, HTTPStatus.NOT_FOUND: ErrorSchema})
def delete_user(request, username: str):
    try:
        user = get_object_or_404(User, username=username)
        user.delete()
        return HTTPStatus.NO_CONTENT, None
    except Http404:
        return HTTPStatus.NOT_FOUND, ErrorSchema(detail="User not found")
    except Exception as e:
        return HTTPStatus.FORBIDDEN, ErrorSchema(detail=str(e))