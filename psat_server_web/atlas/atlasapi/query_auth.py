from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from re import match

class QueryAuthentication(authentication.TokenAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('token')

        if not token:
            return None

        if not match("^\w+$", token):
            msg = 'Invalid token format.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)
