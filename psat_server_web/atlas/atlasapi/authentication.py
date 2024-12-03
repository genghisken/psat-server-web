from re import match
import logging

from django.conf import settings
from django.utils.timezone import now
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Token authentication using the ExpiringToken model, which has an expiry 
    date and must be refreshed manually or automatically.
    
    The token is passed in the Authorization header as 'Token <key>'.
    """
    model = Token

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        
        # Retrieve the user's group and get the token expiration time from the group profile
        if user.groups.exists():
            try:
                group_profile = user.groups.first().profile
            except AttributeError:
                msg = 'Could not authenticate: Group has no profile. Please contact administrator.'
                logger.error(msg)
                raise AuthenticationFailed(msg)
            token_expiration_time = group_profile.token_expiration_time.total_seconds()
        else:
            # Otherwise use the default expiration time
            token_expiration_time = settings.TOKEN_EXPIRY
        
        # Calculate the token's age and compare it to the expiration setting
        token_age = (now() - token.created).total_seconds()
        if token_age > token_expiration_time:
            logger.warning(f'User {user} attempted to use an expired token.')
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