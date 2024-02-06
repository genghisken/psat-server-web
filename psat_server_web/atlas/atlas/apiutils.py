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

    transient = AtlasDiffObjects.objects.get(pk=atlas_diff_objects_id)

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
        if listId > 0 and listId <= 100:
            if dateThreshold is not None:
                sys.stderr.write("\nDATE THRESHOLD = %s\n" % dateThreshold)
                querySet = WebViewUserDefined.objects.filter(object_group_id = listId, followup_flag_date__gt = dateThreshold)
            else:
                querySet = WebViewUserDefined.objects.filter(object_group_id = listId)
    else:
        # There are currently 11 valid lists.
        if listId >= 0 and listId <= 11:
            if dateThreshold is not None:
                sys.stderr.write("\nDATE THRESHOLD = %s\n" % dateThreshold)
                querySet = followupClassList[int(listId)].objects.filter(followup_flag_date__gt = dateThreshold)
            else:
                querySet = followupClassList[int(listId)].objects.all()

    objectList = []

    if querySet is not None:
        for row in querySet:
            objectList.append(model_to_dict(row))

    return objectList
