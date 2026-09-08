from django.forms.models import model_to_dict

from .dbviews import WebViewUserDefined
from .views import followupClassList
from .models import TcsObjectGroups


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
