from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from .serializers import ConeSerializer
from .authentication import QueryAuthentication, ExpiringTokenAuthentication
from .permissions import HasReadAccess, HasWriteAccess
from django.core.exceptions import ObjectDoesNotExist
import sys

def retcode(message):
    if 'error' in message: return status.HTTP_400_BAD_REQUEST
    else:                  return status.HTTP_200_OK

class ObtainExpiringAuthToken(ObtainAuthToken):
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Get the expiration time from the user's group profile
        if user.groups.exists():
            group_profile = user.groups.first().profile
            token_expiration_time = group_profile.token_expiration_time.total_seconds()
        else:
            # If the user is not assigned to a group, use the default setting
            token_expiration_time = settings.TOKEN_EXPIRY

        # Check if token is expired based on `created` field and the setting
        token_age = (now() - token.created).total_seconds()
        if token_age > token_expiration_time:
            # If expired, delete the token and create a new one
            token.delete()
            token = Token.objects.create(user=user)
            # Update the token age for return
            token_age = (now() - token.created).total_seconds()
            created = True

        return Response({
            'token': token.key,
            'expires_in': token_expiration_time - token_age,
            'refreshed': created,
        })

# 2024-10-15 KWS Introduced the first API call for Pan-STARRS. Cone searching.
class ConeView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = ConeSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ConeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
