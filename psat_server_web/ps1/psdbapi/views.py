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
from .serializers import (
    ConeSerializer,
    ObjectListSerializer,
    TcsObjectGroupsSerializer,
    TcsObjectGroupsDeleteSerializer,
    TcsObjectGroupsListSerializer,
    ExternalCrossmatchesListSerializer,
    ObjectDetectionListSerializer,
    ObjectsSerializer,
)
from .authentication import QueryAuthentication, ExpiringTokenAuthentication
from .permissions import HasReadAccess, HasWriteAccess
from django.core.exceptions import ObjectDoesNotExist
from psdb.models import TcsAPIUsageLog
import sys

def retcode(message):
    if 'error' in message: return status.HTTP_400_BAD_REQUEST
    else:                  return status.HTTP_200_OK

# 2026-09-08 KWS Claude wrote this. All code here reviewed by KWS.
#                See TODO list.

# 2026-09-28 KWS LoggingAPIView is identical to the ATLAS version.
class LoggingAPIView(APIView):
    def log_request(self, validated_data):
        summary_dict = {}
        for key in validated_data.keys():
            if not isinstance(validated_data[key], str):
                summary_dict[key] = validated_data[key]
                continue
            if len(validated_data[key]) <= 1280:
                summary_dict[key] = validated_data[key]
                continue
            summary_dict[key + "_count"] = len(validated_data[key].split(','))

        TcsAPIUsageLog.objects.create(
            user=str(self.request.user),
            endpoint=self.request.path,
            validated_data=summary_dict,
        )

# 2026-09-28 KWS ObtainExpiringAuthToken identical to the ATLAS version. 
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
class ConeView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = ConeSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ConeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2026-09-28 KWS ObjectListView identical to the ATLAS version. 
class ObjectListView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = ObjectListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ObjectListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2026-09-28 KWS TcsObjectGroupsView identical to the ATLAS version. 
class TcsObjectGroupsView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = TcsObjectGroupsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2026-09-28 KWS TcsObjectGroupsDeleteView almost identical to the ATLAS version. Some slight logic changes.
#                TODO: Verify that the logic works correctly. What happens when you try to delete a group
#                      that does not exist? (Just HTTP_400_BAD_REQUEST I think, which is fine.) Note that we
#                      don't currently have requirements to delete any groups. But we must test this.
class TcsObjectGroupsDeleteView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = TcsObjectGroupsDeleteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if "deleted" in message['info']:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


# 2026-09-28 KWS TcsObjectGroupsListView identical to the ATLAS version. 
class TcsObjectGroupsListView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = TcsObjectGroupsListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = TcsObjectGroupsListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2026-09-28 KWS ExternalCrossmatchesListView identical to the ATLAS version. 
class ExternalCrossmatchesListView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = ExternalCrossmatchesListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ExternalCrossmatchesListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2026-09-28 KWS ObjectDetectionListView similar to the ATLAS version but for some reason we skipped the GET
#                version of the code. Since there is no reason to skip it, I've restored it to be identical
#                to the ATLAS version. (Perhaps the ATLAS one is in fact incorrect.)
#                TODO: Check why we need write access to use this method.
class ObjectDetectionListView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasWriteAccess]

    def get(self, request):
        serializer = ObjectDetectionListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ObjectDetectionListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2026-09-28 KWS ObjectsView identical to the ATLAS version. 
class ObjectsView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = ObjectsSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ObjectsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
