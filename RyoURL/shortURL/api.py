from ninja import NinjaAPI
from ninja.renderers import JSONRenderer
from django.core.serializers.json import DjangoJSONEncoder

from pydantic import AnyUrl

from .apis.auth import JWTAuth
from .apis.auth_api import auth_router
from .apis.short_url_basic_api import short_url_router
from .apis.short_url_with_auth_api import auth_short_url_router
from .apis.user_api import user_router
from .apis.admin_api import admin_router

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, AnyUrl): 
            return str(obj)
        return super().default(obj)

class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder

api = NinjaAPI(renderer=CustomJSONRenderer(), auth=JWTAuth())

api.add_router("/auth/", auth_router)
api.add_router("/short-url/", short_url_router)
api.add_router("/short-url-with-auth/", auth_short_url_router)
api.add_router("/user/", user_router)
api.add_router("/admin/", admin_router)