# Functions within this file are too Django-specific to include in 'utils'.

# PS1 version of the Django Search Form Helper Function.

from psdb.models import TcsTransientObjects
from psdb.models import TcsImages
from gkutils.commonutils import getObjectNamePortion, getCoordsAndSearchRadius, coneSearchHTM, FULL
from django.db.models import Q    # Need Q objects for OR query
import sys

def processSearchForm(searchText, getAssociatedData = False):
    """processSearchForm.

    Args:
        searchText:
        getAssociatedData:
    """
    from django.db import connection

    results = []
    # Is it a name?
    name = getObjectNamePortion(searchText)
    if name:
         # Do a name search
        if name.startswith('20'):
            results = TcsTransientObjects.objects.filter(Q(other_designation__isnull = False) & Q(other_designation__startswith = name))
        elif name.startswith('PS'):
            results = TcsTransientObjects.objects.filter(Q(ps1_designation__isnull = False) & Q(ps1_designation__startswith = name))
        else:
            results = TcsTransientObjects.objects.filter(Q(ps1_designation__isnull = False) & (Q(ps1_designation__startswith = 'PS' + name) | Q(ps1_designation__startswith = 'PS1-' + name) | Q(other_designation__startswith = '20' + name)))
    else:
         # It must be a coordinate
         coords = getCoordsAndSearchRadius(searchText)
         searchRadius = 4.0
         if coords['radius']:
             searchRadius = float(coords['radius'])
             if searchRadius > 99.0:
                  searchRadius = 99.0
         
         message, xmObjects = coneSearchHTM(coords['ra'], coords['dec'], searchRadius, 'tcs_transient_objects', queryType = FULL, conn = connection, django = True)
         for xm in xmObjects:
             dictRow = xm[1]
             dictRow.update({'separation': xm[0]})
             # 2016-08-29 KWS Higly inefficient database usage, but because we are bypassing Django model
             #                we need to manually collect the foreign key data.  E.g. images and latest
             #                object stats.
             if getAssociatedData:
                 if dictRow['tcs_images_id']:
                     # Get images
                     images = TcsImages.objects.get(pk=dictRow['tcs_images_id'])
                     if images:
                         dictRow.update({'tcs_images_id': images})
             results.append(dictRow)

    return results

import socket
# 2019-08-07 KWS added sendMessage to send a message to a listening daemon. This might be for:
#                * getting a PS name
#                * registering on TNS
#                * doing a minor planet check.

def sendMessage(host, port, message):
    '''
    Send a message to a listener.
    '''

    response = None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(message.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        s.close()
    except socket.error as e:
        sys.stderr.write("Cannot connect. Maybe the service has not been started or is listening on a different port.\n")
        sys.stderr.write("%s" % str(e))

    return response

def filterGetParameters(request, queryFilter, prefix = ''):
    """filterGetParameters.

    Args:
        request:
        queryFilter:
        prefix:
    """
    # When we're querying for tcs_transient_objects we probably have lots of
    # common things to pull out.  Hence this helper function. Prefix can
    # be used if we need to refer the parameters remotely, but note that it
    # applies to all parameters at the moment.

    # 2020-10-13 KWS Add ability to do greater than, greater than or equal to,
    #                less than, less than or equal to.
    import datetime
    flagDate = None
    flagParameter = 'followup_flag_date'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        flagParameter = 'followup_flag_date' + suffix
        flagDate = request.GET.get(flagParameter)
        if flagDate is not None:
            break

    try:
        flagDate = datetime.datetime.strptime(flagDate, "%Y-%m-%d").date()
    except ValueError as e:
        flagDate = None
    except TypeError as e:
        flagDate = None

    if flagDate:
        queryFilter[prefix + flagParameter] = flagDate

    # 2020-10-13 KWS Added rb_pix (i.e. RB factor)
    zooniverseScore = None
    zooniverseScoreParameter = 'zooniverse_score'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        zooniverseScoreParameter = 'zooniverse_score' + suffix
        zooniverseScore = request.GET.get(zooniverseScoreParameter)
        if zooniverseScore is not None:
            break

    try:
        zooniverseScore = float(zooniverseScore)
    except ValueError as e:
        zooniverseScore = None
    except TypeError as e:
        zooniverseScore = None

    if zooniverseScore:
        queryFilter[prefix + zooniverseScoreParameter] = zooniverseScore

    # 2020-10-13 KWS Added rb_pix (i.e. RB factor)
    rbPix = None
    rbPixParameter = 'rb_pix'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        rbPixParameter = 'rb_pix' + suffix
        rbPix = request.GET.get(rbPixParameter)
        if rbPix is not None:
            break

    try:
        rbPix = float(rbPix)
    except ValueError as e:
        rbPix = None
    except TypeError as e:
        rbPix = None

    if rbPix:
        queryFilter[rbPixParameter] = rbPix

    # 2020-12-11 KWS Added rb_cat (i.e. catalogue RB factor)
    rbCat = None
    rbCatParameter = 'rb_cat'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        rbCatParameter = 'rb_cat' + suffix
        rbCat = request.GET.get(rbCatParameter)
        if rbCat is not None:
            break

    try:
        rbCat = float(rbCat)
    except ValueError as e:
        rbCat = None
    except TypeError as e:
        rbCat = None

    if rbCat:
        queryFilter[rbCatParameter] = rbCat

    # 2020-12-11 KWS Added earliest mag & latest mag
    latestMag = None
    latestMagParameter = 'latest_mag'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        latestMagParameter = 'latest_mag' + suffix
        latestMag = request.GET.get(latestMagParameter)
        if latestMag is not None:
            break

    try:
        latestMag = float(latestMag)
    except ValueError as e:
        latestMag = None
    except TypeError as e:
        latestMag = None

    if latestMag:
        queryFilter[latestMagParameter] = latestMag


    # 2020-12-11 KWS Added earliest mag & earliest mag
    earliestMag = None
    earliestMagParameter = 'earliest_mag'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        earliestMagParameter = 'earliest_mag' + suffix
        earliestMag = request.GET.get(earliestMagParameter)
        if earliestMag is not None:
            break

    try:
        earliestMag = float(earliestMag)
    except ValueError as e:
        earliestMag = None
    except TypeError as e:
        earliestMag = None

    if earliestMag:
        queryFilter[earliestMagParameter] = earliestMag


    # 2020-12-11 KWS Added earliest mag & earliest mag
    earliestMJD = None
    earliestMJDParameter = 'earliest_mjd'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        earliestMJDParameter = 'earliest_mjd' + suffix
        earliestMJD = request.GET.get(earliestMJDParameter)
        if earliestMJD is not None:
            break

    try:
        earliestMJD = float(earliestMJD)
    except ValueError as e:
        earliestMJD = None
    except TypeError as e:
        earliestMJD = None

    if earliestMJD:
        queryFilter[earliestMJDParameter] = earliestMJD


    # 2020-12-11 KWS Added latest mag & latest mag
    latestMJD = None
    latestMJDParameter = 'latest_mjd'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        latestMJDParameter = 'latest_mjd' + suffix
        latestMJD = request.GET.get(latestMJDParameter)
        if latestMJD is not None:
            break

    try:
        latestMJD = float(latestMJD)
    except ValueError as e:
        latestMJD = None
    except TypeError as e:
        latestMJD = None

    if latestMJD:
        queryFilter[latestMJDParameter] = latestMJD


    # 2020-12-11 KWS Added earliest mag & earliest mag
    otherDesignation = None
    otherDesignationParameter = 'other_designation'
    for suffix in ['__startswith', '__endswith', '']:
        otherDesignationParameter = 'other_designation' + suffix
        otherDesignation = request.GET.get(otherDesignationParameter)
        if otherDesignation is not None:
            break

    if otherDesignation:
        queryFilter[otherDesignationParameter] = otherDesignation


    objectType = None
    objectType = request.GET.get('object_classification')
    try:
        objectType = int(objectType)
    except ValueError as e:
        objectType = None
    except TypeError as e:
        objectType = None

    if objectType:
        queryFilter[prefix + 'object_classification'] = objectType

    sherlockType = None
    sherlockType = request.GET.get('sherlockClassification')

    if sherlockType:
        queryFilter[prefix + 'sherlockClassification'] = sherlockType

    specType = None
    specType = request.GET.get('observation_status')

    if specType:
        queryFilter[prefix + 'observation_status'] = specType

    xt = None
    xtParameter = 'xt'

    for suffix in ['__isnull', '']:
        xtParameter = 'xt' + suffix
        xt = request.GET.get(xtParameter)
        if xt is not None:
            break

    try:
        xt = int(xt)
    except ValueError as e:
        xt = None
    except TypeError as e:
        xt = None

    if xt:
        queryFilter[prefix + xtParameter] = xt

    return queryFilter

def getDjangoTables2ImageTemplate(imageType):
    IMAGE_TEMPLATE = """<img id="stampimages" src="{{ MEDIA_URL }}images/data/{{ dbname }}/{{ record.tcs_images_id.whole_mjd }}/{{ record.tcs_images_id.%s }}.jpeg" alt="triplet" title="{{ record.tcs_images_id.pss_filename }}" onerror="this.src='{{ STATIC_URL }}images/image_not_available.jpeg';" height="200" />""" % imageType
    return IMAGE_TEMPLATE

