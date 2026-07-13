from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.throttling import AnonRateThrottle

# 2024-01-29 KWS Need the model to do inserts.
from atlas.models import TcsObjectGroups, TcsVraScores, TcsAPIUsageLog
from .serializers import (
    ConeSerializer, 
    ObjectsSerializer, 
    ObjectListSerializer, 
    VRAScoresSerializer, 
    VRAScoresListSerializer, 
    VRATodoSerializer, 
    VRATodoListSerializer, 
    TcsObjectGroupsSerializer, 
    TcsObjectGroupsDeleteSerializer, 
    TcsObjectGroupsListSerializer, 
    VRARankSerializer, 
    VRARankListSerializer, 
    ExternalCrossmatchesListSerializer,
    ObjectDetectionListSerializer,
)
from .authentication import QueryAuthentication, ExpiringTokenAuthentication
from .permissions import HasReadAccess, HasWriteAccess

def retcode(message):
    if 'error' in message: return status.HTTP_400_BAD_REQUEST
    else:                  return status.HTTP_200_OK
    
### HELOISE SHENANIGANS EXPLORING LOGGING API USAGE ####
class LoggingAPIView(APIView):
    def log_request(self, validated_data):
        ### Need to use my model TcsAPIUsageLog to fill in the 
        ### values in the DB
        summary_dict = {}
        for key in validated_data.keys():
            if not isinstance(validated_data[key], str):
                summary_dict[key] = validated_data[key]
                continue

            if len(validated_data[key]) <= 1280: 
                # corresponds to 64 ATLAS ID + their commas
                # Could have used .split but then less general
                # if we have another string field later that can grow very big this won't work
                summary_dict[key] = validated_data[key]
                continue
            else:
                # The summary REMAINS comma separated because in general the large
                # fields are lists of ATLAS IDs. So for the biggest use case thats
                # the summary info I absolutely want
                summary_dict[key+"_count"] = len(validated_data[key].split(','))

        TcsAPIUsageLog.objects.create(
            user = str(self.request.user),
            endpoint = self.request.path, #always a string
            validated_data=summary_dict
        )




### END HELOISE SHENANIGANS ###


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


class VRAScoresView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = VRAScoresSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)

            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VRAScoresListView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = VRAScoresListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = VRAScoresListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2024-04-16 KWS Added VRATodoView. NOTE: Add code to read the reply message and generate a sensible HTTP response
#                appropriate to the circumstances. E.g. if object is not found generate a 404, etc.
class VRATodoView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = VRATodoSerializer(data=request.data, context={'request': request})
    
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
    
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
# 2024-05-07 KWS Added VRATodoListView.
class VRATodoListView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = VRATodoListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = VRATodoListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class TcsObjectGroupsDeleteView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    # TODO: Change this to HasDeleteAccess?
    permission_classes = [IsAuthenticated&HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = TcsObjectGroupsDeleteSerializer(data=request.data, context={'request': request})
    
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            
        if "deleted" in message['info']:
            # No point returning the message info. 204s will drop the message content anyway.
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif "does not exist" in message['info']:
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2024-05-22 KWS Added VRARankView. NOTE: Add code to read the reply message and generate a sensible HTTP response
#                appropriate to the circumstances. E.g. if object is not found generate a 404, etc.
class VRARankView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = VRARankSerializer(data=request.data, context={'request': request})
    
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
# 2024-05-22 KWS Added VRARankListView.
class VRARankListView(LoggingAPIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated&HasReadAccess]

    def get(self, request):
        serializer = VRARankListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = VRARankListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            self.log_request(serializer.validated_data)
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2024-09-24 KWS Added ExternalCrossmatchesListView.
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


# 2024-09-24 KWS Added ExternalCrossmatchesListView.
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

