from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from ninja.errors import HttpError
from http import HTTPStatus
from ..models import User

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        if not token:
            return self.get_anonymous_auth()
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            auth = {
                'user': user,
                'user_type': user.user_type
            }
            return auth
        except Exception:
            return self.get_anonymous_auth()

    def get_anonymous_auth(self):
        anonymous_user, _ = User.objects.get_or_create(
            username='anonymous',
            defaults={'user_type': 0}
        )
        return {
            'user': anonymous_user,
            'user_type': 0
        }
    
    def admin_check(self, auth):
        return auth['user_type'] == 2
    
    def user_check(self, auth):
        return auth['user_type'] > 0

class AdminJWTAuth(JWTAuth):
    def authenticate(self, request, token):
        auth = super().authenticate(request, token)
        if not self.admin_check(auth):
            raise HttpError(HTTPStatus.FORBIDDEN, "需要管理員權限")
        return auth