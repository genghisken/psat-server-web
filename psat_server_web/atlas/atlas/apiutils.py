from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout as RequestsConnectionTimeoutError
from django.conf import settings
from atlas.models import AtlasDiffObjects
from atlas.models import AtlasForcedPhotometry
from atlas.models import TcsGravityEventAnnotations
from atlas.models import SherlockClassifications
from atlas.models import SherlockCrossmatches
from atlas.models import TcsObjectComments
from atlas.models import TcsCrossMatchesExternal
from atlas.models import AtlasDetectionsddc
from atlas.models import TcsVraScores
from atlas.models import TcsVraTodo
from atlas.models import TcsObjectGroups
from atlas.models import TcsVraRank
from django.forms.models import model_to_dict
from .lightcurvequeries import *
from .views import followupClassList
from .views import WebViewUserDefined
from .views import AtlasDetectionsddcTable
from .commonqueries import getNonDetectionsUsingATLASFootprint, ATLAS_METADATADDC, filterWhereClauseddc, LC_POINTS_QUERY_ATLAS_DDC, FILTERS, getLightcurvePoints, getLightcurvePointsDDCAPI, getNonDetectionsUsingATLASFootprintAPI
from .dbviews import CustomLCBlanks, CustomLCPoints, CustomLCPoints2, CustomLCBlanks2

from .views import LC_LIMITS, LC_LIMITS_MD
import numpy as np
import sys
from django.core.exceptions import ObjectDoesNotExist

def candidateddcApi(request, atlas_diff_objects_id, mjdThreshold = None):
    """candidateddcApi.

    Args:
        request:
        atlas_diff_objects_id:
        mjdThreshold:
    """

    from django.db import connection
    import sys

    # 2021-10-21 KWS Use the Lasair API to do a cone search so we can check for nearby ZTF objects
    from lasair import LasairError, lasair_client as lasair


    try:
        transient = AtlasDiffObjects.objects.get(pk=atlas_diff_objects_id)
    except ObjectDoesNotExist as e:
        # 2025-11-14 KWS Return an empty object if the object does not exist.
        # This protects the API from generating a 500 error if a bogus object
        # is sent. But since the keys are the same the client code should be
        # able to read and interpet this result.
        data = {
            'object': e.to_dict() if hasattr(e, 'to_dict') else str(e),
            'lc': None,
            'lcnondets': None,
            'fp': None,
            'sherlock_crossmatches': None,
            'sherlock_classifications': None,
            'tns_crossmatches': None,
            'external_crossmatches': None,
        }
        return data


    # 2017-03-21 KWS Get Gravity Wave annotations and Sherlock Classifications
    sc = SherlockClassifications.objects.filter(transient_object_id_id = transient.id)
    # 2017-11-07 KWS Get Sherlock Crossmatches
    sx = SherlockCrossmatches.objects.filter(transient_object_id_id = transient.id)
    gw = TcsGravityEventAnnotations.objects.filter(transient_object_id_id = transient.id).filter(enclosing_contour__lt=100)
    #existingComments = TcsObjectComments.objects.filter(transient_object_id = transient.id).order_by('date_inserted')

    # 2013-10-30 KWS Get external crossmatches if they exist
    externalXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id = transient.id).exclude(matched_list = 'Transient Name Server').order_by('external_designation')

    # 2019-10-18 KWS Get TNS crossmatch if it exists. Yes - another unnecessary hit to the database, but quick.
    tnsXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id = transient.id, matched_list = 'Transient Name Server')

    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    try:
        detectionLimits = LC_LIMITS[dbName]
    except KeyError as e:
        # Default detections limits for medium deep
        detectionLimits = LC_LIMITS_MD

    if mjdThreshold is not None:
        forcedPhotometry = AtlasForcedPhotometry.objects.filter(atlas_object_id = transient.id).filter(mjd_obs__gte=mjdThreshold).order_by('mjd_obs')
    else:
        forcedPhotometry = AtlasForcedPhotometry.objects.filter(atlas_object_id = transient.id).order_by('mjd_obs')


    recsExperiment = getLightcurvePointsDDCAPI(transient.id, djangoRawObject = CustomLCPoints2, lcQuery=LC_POINTS_QUERY_ATLAS_DDC + filterWhereClauseddc(FILTERS), conn = connection, mjdThreshold = mjdThreshold)
    blanksExperiment = getNonDetectionsUsingATLASFootprintAPI(recsExperiment, djangoRawObject = CustomLCBlanks2, ndQuery=ATLAS_METADATADDC, filterWhereClause = filterWhereClauseddc, catalogueName = 'atlas_metadataddc', conn = connection, mjdThreshold = mjdThreshold, transient = transient)


    # 2024-02-05 KWS The model_to_dict method doesn't pull out any @property methods
    #                from the model, so need to iterate through and add them. Since
    #                we need to iterate anyway, this should not slow things down.
    forcedWithProperties = []
    for f in forcedPhotometry:
        fp = model_to_dict(f)
        fp['uJy'] = f.uJy
        fp['duJy'] = f.duJy
        fp['texp'] = f.texp
        forcedWithProperties.append(fp)

    data = {
            'object': model_to_dict(transient),
            'lc': [model_to_dict(r) for r in recsExperiment],
            'lcnondets': [model_to_dict(b) for b in blanksExperiment],
            'fp': forcedWithProperties,
            'sherlock_crossmatches': [model_to_dict(s) for s in sx],
            'sherlock_classifications': [model_to_dict(s) for s in sc],
            'tns_crossmatches': [model_to_dict(t) for t in tnsXMs],
            'external_crossmatches': [model_to_dict(e) for e in externalXMs]
           }

    return data


def getObjectList(request, listId, getCustomList = False, dateThreshold = None):

    querySet = None

    if getCustomList:
        if dateThreshold is not None:
            querySet = WebViewUserDefined.objects.filter(object_group_id = listId, followup_flag_date__gt = dateThreshold)
        else:
            querySet = WebViewUserDefined.objects.filter(object_group_id = listId)
    else:
        # There are currently 11 valid lists.
        if dateThreshold is not None:
            querySet = followupClassList[int(listId)].objects.filter(followup_flag_date__gt = dateThreshold)
        else:
            querySet = followupClassList[int(listId)].objects.all()

    objectList = []

    if querySet is not None:
        for row in querySet:
            objectList.append(model_to_dict(row))

    return objectList


def getVRAScoresList(request, objects = [], debug = False, dateThreshold = None, idThreshold = 0):

    vraScoresList = []

    # If we specify objects then ignore any thresholds. Deprecated flag is common to all objects.
    # If you don't want a common debug flag, then request objects one at a time!
    if len(objects) > 0:
        for objectid in objects:
            try:
                oid = int(objectid)
            except ValueError as e:
                continue

            try:
                querySet = TcsVraScores.objects.filter(transient_object_id_id=oid, debug=debug)
                if querySet is not None:
                    for vra in querySet:
                        vraScoresList.append(model_to_dict(vra))
            except ObjectDoesNotExist as e:
                # Silent fail. No objects returned if the object does not exist.
                pass
    else:
        querySet = TcsVraScores.objects.filter(pk__gte=idThreshold).filter(timestamp__gte=dateThreshold)
        #querySet = TcsVraScores.objects.all()
        if querySet is not None:
            for vra in querySet:
                vraScoresList.append(model_to_dict(vra))

    return vraScoresList


# 2024-05-07 KWS Added getVRATodoList
def getVRATodoList(request, objects = [], dateThreshold = None, idThreshold = 0):

    vraTodoList = []

    # If we specify objects then ignore any thresholds. Deprecated flag is common to all objects.
    if len(objects) > 0:
        for objectid in objects:
            try:
                oid = int(objectid)
            except ValueError as e:
                continue

            try:
                querySet = TcsVraTodo.objects.filter(transient_object_id_id=oid)
                if querySet is not None:
                    for vra in querySet:
                        vraTodoList.append(model_to_dict(vra))
            except ObjectDoesNotExist as e:
                # Silent fail. No objects returned if the object does not exist.
                pass
    else:
        querySet = TcsVraTodo.objects.filter(pk__gte=idThreshold).filter(timestamp__gte=dateThreshold)
        #querySet = TcsVraTodo.objects.all()
        if querySet is not None:
            for vra in querySet:
                vraTodoList.append(model_to_dict(vra))

    return vraTodoList


# 2024-05-20 KWS Added getCustomListObjects
def getCustomListObjects(request, objectid = None, objectgroupid = None):

    customListObjects = []

    if objectid is None and objectgroupid is not None:
        querySet = TcsObjectGroups.objects.filter(object_group_id = objectgroupid)
    elif objectid is not None and objectgroupid is None:
        querySet = TcsObjectGroups.objects.filter(transient_object_id__id = objectid)
    else:
        querySet = TcsObjectGroups.objects.all()

    if querySet is not None:
        for row in querySet:
            customListObjects.append(model_to_dict(row))

    return customListObjects

# 2024-05-07 KWS Added getVRARankList
def getVRARankList(request, objects = [], dateThreshold = None, idThreshold = 0):

    vraRankList = []

    # If we specify objects then ignore any thresholds. Deprecated flag is common to all objects.
    if len(objects) > 0:
        for objectid in objects:
            try:
                oid = int(objectid)
            except ValueError as e:
                continue

            try:
                querySet = TcsVraRank.objects.filter(transient_object_id_id=oid)
                if querySet is not None:
                    for vra in querySet:
                        vraRankList.append(model_to_dict(vra))
            except ObjectDoesNotExist as e:
                # Silent fail. No objects returned if the object does not exist.
                pass
    else:
        querySet = TcsVraRank.objects.filter(pk__gte=idThreshold).filter(timestamp__gte=dateThreshold)
        #querySet = TcsVraRank.objects.all()
        if querySet is not None:
            for vra in querySet:
                vraRankList.append(model_to_dict(vra))

    return vraRankList


# 2024-09-24 KWS Added getExternalCrossmatches
def getExternalCrossmatchesList(request, externalObjects = []):

    externalCrossmatchesList = []

    for xm in externalObjects:
        miniList = []
        querySet = TcsCrossMatchesExternal.objects.filter(external_designation=xm)
        if querySet is not None:
            for x in querySet:
                miniList.append(model_to_dict(x))
            externalCrossmatchesList.append(miniList)

    return externalCrossmatchesList
