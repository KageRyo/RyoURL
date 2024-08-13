from typing import List
from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from ..models import Url
from .auth import JWTAuth
from .schemas import UrlSchema, ErrorSchema, CustomUrlCreateSchema
from .short_url_basic_api import handle_domain, create_url_entry

short_url_auth = JWTAuth()

class AuthRouter(Router):
    def get_permissions(self, request):
        if not short_url_auth.user_check(short_url_auth.authenticate(request, request.headers.get('Authorization', '').split(' ')[-1])):
            raise HttpError(403, "需要登入")

auth_short_url_router = AuthRouter(tags=["auth-short-url"])

@auth_short_url_router.post("custom", response={201: UrlSchema, 400: ErrorSchema, 403: ErrorSchema})
def create_custom_url(request, data: CustomUrlCreateSchema):
    short_url = handle_domain(request, data.short_string)
    if Url.objects.filter(short_string=data.short_string).exists():
        return 400, {"message": "自訂短網址已存在，請更換其他短網址。"}
    
    try:
        url = create_url_entry(data.origin_url, data.short_string, short_url, data.expire_date, user=request.auth['user'])
        return 201, UrlSchema(
            origin_url=url.origin_url,
            short_string=url.short_string,
            short_url=url.short_url,
            create_date=url.create_date,
            expire_date=url.expire_date,
            visit_count=url.visit_count,
            creator_username=url.user.username if url.user else None
        )
    except Exception as e:
        return 400, {"message": str(e)}

@auth_short_url_router.get('all-my', response={200: List[UrlSchema], 403: ErrorSchema})
def get_all_myurl(request):
    urls = Url.objects.filter(user=request.auth['user'])
    return 200, [UrlSchema(
        origin_url=url.origin_url,
        short_string=url.short_string,
        short_url=url.short_url,
        create_date=url.create_date,
        expire_date=url.expire_date,
        visit_count=url.visit_count,
        creator_username=url.user.username if url.user else None
    ) for url in urls]

@auth_short_url_router.delete('url/{short_string}', response={204: None, 404: ErrorSchema, 403: ErrorSchema})
def delete_short_url(request, short_string: str):
    url = get_object_or_404(Url, short_string=short_string)
    if url.user == request.auth['user'] or short_url_auth.admin_check(request.auth):
        url.delete()
        return 204, None
    return 403, {"message": "無權限刪除此短網址"}