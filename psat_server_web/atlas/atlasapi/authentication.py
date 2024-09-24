from re import match

from django.conf import settings
from django.utils.timezone import now
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Token authentication using the ExpiringToken model, which has an expiry 
    date and must be refreshed manually or automatically.
    
    The token is passed in the Authorization header as 'Token <key>'.
    """
    model = Token

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        
        # Calculate the token's age and compare it to the expiration setting
        token_age = (now() - token.created).total_seconds()
        if token_age > settings.TOKEN_EXPIRY:
            raise AuthenticationFailed('Token has expired.')
        
        return user, token
    

class QueryAuthentication(ExpiringTokenAuthentication):
    """
    Token authentication using query parameters.
    """
    def authenticate(self, request):
        token = request.query_params.get('token')

        if not token:
            return None

        if not match("^\w+$", token):
            msg = 'Invalid token format.'
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)