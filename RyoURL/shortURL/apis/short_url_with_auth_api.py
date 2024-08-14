from typing import List
from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from rest_framework import status
from django.db import IntegrityError

from ..models import Url
from .auth import JWTAuth
from .schemas import UrlSchema, ErrorSchema, CustomUrlCreateSchema
from .short_url_basic_api import handle_domain, create_url_entry

short_url_auth = JWTAuth()

class AuthRouter(Router):
    def get_permissions(self, request):
        auth = short_url_auth.authenticate(request, request.headers.get('Authorization', '').split(' ')[-1])
        if not short_url_auth.user_check(auth):
            raise HttpError(status.HTTP_403_FORBIDDEN, "需要登入")
        request.auth = auth

auth_short_url_router = AuthRouter(tags=["auth-short-url"])

@auth_short_url_router.post("custom", response={status.HTTP_201_CREATED: UrlSchema, status.HTTP_400_BAD_REQUEST: ErrorSchema, status.HTTP_403_FORBIDDEN: ErrorSchema})
def create_custom_url(request, data: CustomUrlCreateSchema):
    short_url = handle_domain(request, data.short_string)
    if Url.objects.filter(short_string=data.short_string).exists():
        raise HttpError(status.HTTP_400_BAD_REQUEST, "自訂短網址已存在，請更換其他短網址。")
    
    user = request.auth['user']
    try:
        url = create_url_entry(data.origin_url, data.short_string, short_url, data.expire_date, user=user)
    except IntegrityError:
        raise HttpError(status.HTTP_400_BAD_REQUEST, "創建短網址失敗，可能是由於資料完整性問題。")
    
    return status.HTTP_201_CREATED, UrlSchema.from_orm(url)

@auth_short_url_router.get('all-my', response={status.HTTP_200_OK: List[UrlSchema], status.HTTP_403_FORBIDDEN: ErrorSchema})
def get_all_myurl(request):
    urls = Url.objects.filter(user=request.auth['user'])
    return status.HTTP_200_OK, [UrlSchema.from_orm(url) for url in urls]

@auth_short_url_router.delete('url/{short_string}', response={status.HTTP_204_NO_CONTENT: None, status.HTTP_404_NOT_FOUND: ErrorSchema, status.HTTP_403_FORBIDDEN: ErrorSchema})
def delete_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    if url.user == request.auth['user'] or short_url_auth.admin_check(request.auth):
        url.delete()
        return status.HTTP_204_NO_CONTENT, None
    raise HttpError(status.HTTP_403_FORBIDDEN, "無權限刪除此短網址")