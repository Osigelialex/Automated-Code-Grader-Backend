from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        
        try:
            validated_token = self.get_validated_token(token)
        except AuthenticationFailed as e:
            if 'Token is invalid or expired' in str(e):
                raise AuthenticationFailed('Your login has expired')
            raise AuthenticationFailed('Invalid authentication token')
        
        try:
            user = self.get_user(validated_token)
            return user, validated_token
        except AuthenticationFailed as e:
            raise AuthenticationFailed(f'Error retrieving user')
