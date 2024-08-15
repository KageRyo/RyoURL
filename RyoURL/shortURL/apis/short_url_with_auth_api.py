from http import HTTPStatus
from typing import List
from ninja import Router
from ninja.errors import HttpError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from ..models import Url
from .auth import JWTAuth
from .schemas import UrlSchema, ErrorSchema, CustomUrlCreateSchema
from .short_url_basic_api import handle_domain, create_url_entry

short_url_auth = JWTAuth()

auth_short_url_router = Router(auth=short_url_auth, tags=["auth-short-url"])


@auth_short_url_router.post("custom", response={HTTPStatus.CREATED: UrlSchema, HTTPStatus.BAD_REQUEST: ErrorSchema, HTTPStatus.FORBIDDEN: ErrorSchema})
def create_custom_url(request, data: CustomUrlCreateSchema):
    short_url = handle_domain(request, data.short_string)
    if Url.objects.filter(short_string=data.short_string).exists():
        raise HttpError(HTTPStatus.BAD_REQUEST, "自訂短網址已存在，請更換其他短網址。")
    
    user = request.auth['user']
    try:
        url = create_url_entry(data.origin_url, data.short_string, short_url, data.expire_date, user=user)
    except IntegrityError:
        raise HttpError(HTTPStatus.BAD_REQUEST, "創建短網址失敗，可能是由於資料完整性問題。")
    
    return HTTPStatus.CREATED, UrlSchema.from_orm(url)

@auth_short_url_router.get('all-my', response={HTTPStatus.OK: List[UrlSchema], HTTPStatus.FORBIDDEN: ErrorSchema})
def get_all_myurl(request):
    urls = Url.objects.filter(user=request.auth['user'])
    return HTTPStatus.OK, [UrlSchema.from_orm(url) for url in urls]

@auth_short_url_router.delete('url/{short_string}', response={HTTPStatus.NO_CONTENT: None, HTTPStatus.NOT_FOUND: ErrorSchema, HTTPStatus.FORBIDDEN: ErrorSchema})
def delete_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    if url.user == request.auth['user'] or short_url_auth.admin_check(request.auth):
        url.delete()
        return HTTPStatus.NO_CONTENT, None
    raise HttpError(HTTPStatus.FORBIDDEN, "無權限刪除此短網址")