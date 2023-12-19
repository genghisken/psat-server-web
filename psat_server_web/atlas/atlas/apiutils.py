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
from .views import AtlasDetectionsddcTable
from .commonqueries import getNonDetectionsUsingATLASFootprint, ATLAS_METADATADDC, filterWhereClauseddc, LC_POINTS_QUERY_ATLAS_DDC, FILTERS, getLightcurvePoints, getLightcurvePointsDDCAPI, getNonDetectionsUsingATLASFootprintAPI
from .dbviews import CustomLCBlanks, CustomLCPoints, CustomLCPoints2, CustomLCBlanks2

from .views import LC_LIMITS, LC_LIMITS_MD
import numpy as np

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

#    dets = AtlasDetectionsddc.objects.filter(atlas_object_id=transient.id)
#    detTable = AtlasDetectionsddcTable(dets)

#    p, recurrences = getLightcurvePoints(transient.id, djangoRawObject = CustomLCPoints, lcQuery=LC_POINTS_QUERY_ATLAS_DDC + filterWhereClauseddc(FILTERS), conn = connection)

    # The first variable below is the list of nondetections for each filter defined by the FILTERS variable in commonqueries.py. Ken to find out what blanks actually contains, since this is actually the raw query object. Why does it need to return the rawQuery object at all???
#    nondets, blanks, lastNonDetection = getNonDetectionsUsingATLASFootprint(recurrences, djangoRawObject = CustomLCBlanks, ndQuery=ATLAS_METADATADDC, filterWhereClause = filterWhereClauseddc, catalogueName = 'atlas_metadataddc', conn = connection)

#    tableHeader = ['id','Ra','Dec','Mag','Dmag','X','Y','Major','Minor','Phi','Det','Chin','Pvr','Ptr','Pmv','Pkn','Pno','Pbn','Pcr','Pxt','Psc','Dup','Wpflx','Dflx','Image_group_id','Mjd','Obs','Mag5sig','Atlas_metadata_id','Texp','Filt','Obj','fpRA','fpDec']

#    django_rows = [r for r in detTable.rows]

#    rows = []
#    for row in django_rows:
#        rows.append([e for e in row])

#    data = {'detection_table': {k: v for k,v in zip(tableHeader, np.array(rows).T)},
#            'lcnondets': {k: np.array(v).T for k,v in zip(FILTERS, nondets)},
#            'fp': [model_to_dict(f) for f in forcedPhotometry],
#            'object': model_to_dict(transient),
#            'sherlock_crossmatches': [model_to_dict(s) for s in sx],
#            'sherlock_classifications': [model_to_dict(s) for s in sc],
#            'tns_crossmatches': [model_to_dict(t) for t in tnsXMs],
#            'external_crossmatches': [model_to_dict(e) for e in externalXMs]
#           }

    data = {
            'object': model_to_dict(transient),
            'lc': [model_to_dict(r) for r in recsExperiment],
            'lcnondets': [model_to_dict(b) for b in blanksExperiment],
            'fp': [model_to_dict(f) for f in forcedPhotometry],
            'sherlock_crossmatches': [model_to_dict(s) for s in sx],
            'sherlock_classifications': [model_to_dict(s) for s in sc],
            'tns_crossmatches': [model_to_dict(t) for t in tnsXMs],
            'external_crossmatches': [model_to_dict(e) for e in externalXMs]
           }

    return data


def getObjectList(request, listId):
    querySet = followupClassList[int(listId)].objects.all()
    objectList = []

    for row in querySet:
        objectList.append(model_to_dict(row))

    return objectList
