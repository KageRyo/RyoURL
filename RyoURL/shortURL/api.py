from ninja import NinjaAPI
from ninja.renderers import JSONRenderer
from django.core.serializers.json import DjangoJSONEncoder

from pydantic import AnyUrl

from .apis.auth_api import auth_router, JWTAuth
from .apis.short_api import url_router

# 自定義 JSON 編碼器和渲染器
class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, AnyUrl): 
            return str(obj)
        return super().default(obj)

# 自定義 JSON 渲染器類別
class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder

# 建立 API 實例，並設定自定義渲染器和 JWT 認證
api = NinjaAPI(renderer=CustomJSONRenderer(), auth=JWTAuth())

# 設定路由（API子路由）
api.add_router("/auth/", auth_router)  # 帳號系統相關 API
api.add_router("/short-url/", url_router)    # 短網址相關 API