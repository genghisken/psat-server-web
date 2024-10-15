from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ConeSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .query_auth import QueryAuthentication
# 2024-10-15 KWS Added Jack's permissions code.
from .permissions import IsApprovedUser
from django.core.exceptions import ObjectDoesNotExist
import sys

def retcode(message):
    if 'error' in message: return status.HTTP_400_BAD_REQUEST
    else:                  return status.HTTP_200_OK

# 2024-10-15 KWS Introduced the first API call for Pan-STARRS. Cone searching.
class ConeView(APIView):
    authentication_classes = [TokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&IsApprovedUser]

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

