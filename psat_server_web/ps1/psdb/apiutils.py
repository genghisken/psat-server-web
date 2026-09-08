from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from .dbviews import WebViewUserDefined, CustomLCPoints
from .views import followupClassList
from .models import TcsObjectGroups, TcsCrossMatchesExternal, TcsTransientObjects, TcsForcedPhotometry, SherlockClassifications, SherlockCrossmatches
from .commonqueries import getLightcurvePoints, getLightcurveNonDetections


OBJECT_LIST_FIELD_TO_LOOKUP = {
    'rb_pix_gte': 'rb_pix__gte',
    'rb_pix_lte': 'rb_pix__lte',
    'ra_gte': 'ra__gte',
    'ra_lte': 'ra__lte',
    'dec_gte': 'dec__gte',
    'dec_lte': 'dec__lte',
    'sherlock_class': 'sherlockClassification',
    'spec_type': 'observation_status',
}

# 2026-09-08 KWS Claude built this - reflects what we have in ATLAS.
def buildObjectListQueryFilter(validated_data):
    queryFilter = {}
    for field, lookup in OBJECT_LIST_FIELD_TO_LOOKUP.items():
        value = validated_data.get(field)
        if value is not None:
            queryFilter[lookup] = value
    return queryFilter


# 2026-09-08 KWS Claude built this - reflects what we have in ATLAS.
def getObjectList(request, listId, getCustomList=False, dateThreshold=None, queryFilter=None):
    if queryFilter is None:
        queryFilter = {}

    if getCustomList:
        filters = {'object_group_id': listId}
        if dateThreshold is not None:
            filters['followup_flag_date__gt'] = dateThreshold
        filters.update(queryFilter)
        querySet = WebViewUserDefined.objects.filter(**filters)
    else:
        filters = {}
        if dateThreshold is not None:
            filters['followup_flag_date__gt'] = dateThreshold
        filters.update(queryFilter)
        querySet = followupClassList[int(listId)].objects.filter(**filters)

    return [model_to_dict(row) for row in querySet]


def getCustomListObjects(request, objectid=None, objectgroupid=None, queryFilter=None):
    querySet = None

    if queryFilter:
        filters = dict(queryFilter)
        if objectgroupid is not None:
            filters['object_group_id'] = objectgroupid
        if objectid is not None:
            filters['id'] = objectid
        matchingIds = list(WebViewUserDefined.objects.filter(**filters).values_list('id', flat=True))
        querySet = TcsObjectGroups.objects.filter(transient_object_id__id__in=matchingIds)
        if objectgroupid is not None:
            querySet = querySet.filter(object_group_id_id=objectgroupid)
    elif objectid is None and objectgroupid is not None:
        querySet = TcsObjectGroups.objects.filter(object_group_id_id=objectgroupid)
    elif objectid is not None and objectgroupid is None:
        querySet = TcsObjectGroups.objects.filter(transient_object_id__id=objectid)

    if querySet is None:
        return []
    return [model_to_dict(row) for row in querySet]


def getExternalCrossmatchesList(request, externalObjects=[]):
    externalCrossmatchesList = []
    for xm in externalObjects:
        querySet = TcsCrossMatchesExternal.objects.filter(external_designation=xm)
        miniList = [model_to_dict(x) for x in querySet]
        if miniList:
            externalCrossmatchesList.append(miniList)
    return externalCrossmatchesList


def _lcPointsToDicts(fullList):
    return [{'mjd': row[0], 'mag': row[1], 'magerr': row[2]} for row in fullList]


def _lcNonDetsToDicts(fullList):
    return [{'mjd': row[0]} for row in fullList]


def transientObjectApi(request, transient_object_id, mjdThreshold=None):
    try:
        transient = TcsTransientObjects.objects.get(pk=transient_object_id)
    except ObjectDoesNotExist as e:
        return {
            'object': str(e),
            'lc': None,
            'lcnondets': None,
            'fp': None,
            'sherlock_crossmatches': None,
            'sherlock_classifications': None,
            'tns_crossmatches': None,
            'external_crossmatches': None,
        }

    sc = SherlockClassifications.objects.filter(transient_object_id_id=transient.id)
    sx = SherlockCrossmatches.objects.filter(transient_object_id_id=transient.id)
    externalXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id=transient.id).exclude(matched_list='Transient Name Server').order_by('external_designation')
    tnsXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id=transient.id, matched_list='Transient Name Server')

    if mjdThreshold is not None:
        forcedPhotometry = TcsForcedPhotometry.objects.filter(transient_object_id=transient.id).filter(mjd_obs__gte=mjdThreshold).order_by('mjd_obs')
    else:
        forcedPhotometry = TcsForcedPhotometry.objects.filter(transient_object_id=transient.id).order_by('mjd_obs')

    *_, lcFullList = getLightcurvePoints(transient.id, djangoRawObject=CustomLCPoints)
    *_, lcNonDetsFullList = getLightcurveNonDetections(transient.id, djangoRawObject=CustomLCPoints)

    return {
        'object': model_to_dict(transient),
        'lc': _lcPointsToDicts(lcFullList),
        'lcnondets': _lcNonDetsToDicts(lcNonDetsFullList),
        'fp': [model_to_dict(f) for f in forcedPhotometry],
        'sherlock_crossmatches': [model_to_dict(s) for s in sx],
        'sherlock_classifications': [model_to_dict(s) for s in sc],
        'tns_crossmatches': [model_to_dict(t) for t in tnsXMs],
        'external_crossmatches': [model_to_dict(e) for e in externalXMs],
    }
