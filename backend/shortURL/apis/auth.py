from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from ninja.errors import HttpError
from http import HTTPStatus
from ..models import User

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        if not token:
            return None
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            return {
                'user': user,
                'user_type': user.user_type
            }
        except Exception:
            return None

class AnonymousAuth:
    def __call__(self, request):
        return {'user': None, 'user_type': 0}

class AdminJWTAuth(JWTAuth):
    def authenticate(self, request, token):
        auth = super().authenticate(request, token)
        if not auth or auth['user_type'] != 2:
            raise HttpError(HTTPStatus.FORBIDDEN, "需要管理員權限")
        return auth