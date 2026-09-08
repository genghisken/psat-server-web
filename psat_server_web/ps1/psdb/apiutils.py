from django.forms.models import model_to_dict

from .dbviews import WebViewUserDefined
from .views import followupClassList


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


def buildObjectListQueryFilter(validated_data):
    queryFilter = {}
    for field, lookup in OBJECT_LIST_FIELD_TO_LOOKUP.items():
        value = validated_data.get(field)
        if value is not None:
            queryFilter[lookup] = value
    return queryFilter


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
