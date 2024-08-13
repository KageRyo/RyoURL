from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from ..models import User

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            request.auth = {
                'user': user,
                'user_type': user.user_type
            }
            return request.auth
        except Exception:
            request.auth = None
            return None