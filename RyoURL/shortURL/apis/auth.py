from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from ..models import User

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            auth = {
                'user': user,
                'user_type': user.user_type
            }
            request.auth = auth
            return auth
        except Exception:
            return None
    
    def user_check(self, auth):
        return auth is not None
    
    def admin_check(self, auth):
        return auth and auth['user_type'] == 2