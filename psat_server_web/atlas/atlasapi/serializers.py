import datetime
import re
import json
import requests
from django.db import IntegrityError
from django.db import connection
from datetime import datetime
from gkutils.commonutils import coneSearchHTM, FULL, QUICK, COUNT, CAT_ID_RA_DEC_COLS, base26, Struct
from rest_framework import serializers
import sys
from atlas.apiutils import candidateddcApi, getObjectList
from django.core.exceptions import ObjectDoesNotExist

# 2024-01-29 KWS Need the model to do inserts.
from atlas.models import TcsVraProbabilities
from atlas.models import AtlasDiffObjects


#CAT_ID_RA_DEC_COLS['objects'] = [['objectId', 'ramean', 'decmean'], 1018]

REQUEST_TYPE_CHOICES = (
    ('count', 'Count'),
    ('all', 'All'),
    ('nearest', 'Nearest'),
)


class ConeSerializer(serializers.Serializer):
    ra = serializers.FloatField(required=True)
    dec = serializers.FloatField(required=True)
    radius = serializers.FloatField(required=True)
    requestType = serializers.ChoiceField(choices=REQUEST_TYPE_CHOICES)

    def save(self):

        ra = self.validated_data['ra']
        dec = self.validated_data['dec']
        radius = self.validated_data['radius']
        requestType = self.validated_data['requestType']

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user

        if radius > 1000:
            replyMessage = "Max radius is 1000 arcsec."
            info = {"error": replyMessage}
            return info

        replyMessage = 'No object found ra=%.5f dec=%.5f radius=%.2f' % (ra, dec, radius)
        info = {"error": replyMessage}

        # Is there an object within RADIUS arcsec of this object? - KWS - need to fix the gkhtm code!!
        # For ATLAS QUICK does not work because of the `dec` syntax error problem. Use FULL until I figure out what
        # needs to be fixed.
        message, results = coneSearchHTM(ra, dec, radius, 'atlas_diff_objects', queryType=FULL, conn=connection, django=True)

        obj = None
        separation = None

        objectList = []
        if len(results) > 0:
            if requestType == "nearest":
                obj = results[0][1]['id']
                separation = results[0][0]
                info = {"object": obj, "separation": separation}
            elif requestType == "all":
                for row in results:
                    objectList.append({"object": row[1]["id"], "separation": row[0]})
                info = objectList
            elif requestType == "count":
                info = {'count': len(results)}
            else:
                info = {"error": "Invalid request type"}

        return info


class ObjectsSerializer(serializers.Serializer):
    objects = serializers.CharField(required=True)
    mjd = serializers.FloatField(required=False, default=None)

    def save(self):
        objects = self.validated_data['objects']
        mjd = self.validated_data['mjd']

        olist = []
        for tok in objects.split(','):
            olist.append(tok.strip())

        if len(olist) > 100:
            return {"info": "Max number of objects for each requests is 100"}
#        olist = olist[:10] # restrict to 10

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user


        result = []
        for candidate in olist:
            result.append(candidateddcApi(request, candidate, mjdThreshold=mjd))
        return result


class ObjectListSerializer(serializers.Serializer):
    objectlistid = serializers.IntegerField(required=True)
    getcustomlist = serializers.BooleanField(required=False, default = False)
    datethreshold = serializers.DateTimeField(required=False, default=None)

    def save(self):
        objectlistid = self.validated_data['objectlistid']
        getcustomlist = self.validated_data['getcustomlist']
        datethreshold = self.validated_data['datethreshold']

        request = self.context.get("request")

        dateThreshold = None
        if datethreshold is not None:
            dateThreshold = self.validated_data['datethreshold']

        objectList = getObjectList(request, objectlistid, getCustomList = getcustomlist, dateThreshold = dateThreshold)
        return objectList


# 2024-01-17 KWS Insert a VRA row for an object. For the time being do this one at a time.
class VRAProbabilitiesSerializer(serializers.Serializer):
    objectid = serializers.IntegerField(required=True)
    preal = serializers.FloatField(required=True)
    pfast = serializers.FloatField(required=True)
    pgal = serializers.FloatField(required=True)
    deprecated = serializers.BooleanField(required=False, default=False)
    insertdate = serializers.DateTimeField(required=False, default=None)


    def save(self):

        from django.conf import settings
        objectid = self.validated_data['objectid']
        preal = self.validated_data['preal']
        pfast = self.validated_data['pfast']
        pgal = self.validated_data['pgal']
        insertdate = self.validated_data['insertdate']
        deprecated = self.validated_data['deprecated']

        insertDate = None
        if insertdate is not None:
            insertDate = self.validated_data['insertdate']

        replyMessage = 'Row created.'

        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = str(request.user)

        if not insertDate:
            insertDate = datetime.now()

        data = {'transient_object_id_id': objectid,
                'preal': preal,
                'pgal': pgal,
                'pfast': pfast,
                'updated': insertDate,
                'deprecated': deprecated,
                'username': userId}

        # Does the objectId actually exit - not allowed to comment on objects that don't exist!
        # This should really return a 404 message.
        try:
            transient = AtlasDiffObjects.objects.get(pk=objectid)
        except ObjectDoesNotExist as e:
            replyMessage = 'Object does not exist.'
            info = { "objectid": objectid, "info": replyMessage }
            return info

        # Does the VRA row exist?
        vra = None
        try:
            vra = TcsVraProbabilities.objects.get(transient_object_id_id=objectid, deprecated=deprecated)
        
        except ObjectDoesNotExist as e:
            # That's OK - we'll create a new object
            pass
        
        if vra:
            instance = vra
        else:
            instance = TcsVraProbabilities(**data)
        try:

            if vra is not None:
                instance.preal = preal
                instance.pfast = pfast
                instance.pgal = pgal
                instance.updated = insertDate
                i = instance.save()
            else:
                i = instance.save()

        except IntegrityError as e:
            replyMessage = 'Duplicate row. Cannot add row.'

        info = { "objectid": objectid, "info": replyMessage }
        return info

