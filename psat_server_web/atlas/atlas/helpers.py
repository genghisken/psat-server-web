# Functions within this file are too Django-specific to include in 'utils'.

# ATLAS version of the Django Search Form Helper Function.

import sys
from atlas.models import AtlasDiffObjects, AtlasDetectionsddc, AtlasDiffDetections
from atlas.models import TcsImages, TcsLatestObjectStats
from gkutils.commonutils import getObjectNamePortion, getCoordsAndSearchRadius, coneSearchHTM, FULL, dbConnect, CAT_ID_RA_DEC_COLS, ra_to_sex, dec_to_sex, Struct
from django.db.models import Q    # Need Q objects for OR query
import socket
from .lightcurvequeries import getLCData, getRecurrenceDataForPlotting

SHOW_LC_DATA_LIMIT = 50

def processSearchForm(searchText, getAssociatedData = False, ddc = False, getNonDets = False, getNearbyObjects = False):
    """processSearchForm.

    Args:
        searchText:
        getAssociatedData:
        ddc:
        getNonDets:
        getNearbyObjects:
    """
    from django.db import connection

    results = []
    # Is it a name?
    name = getObjectNamePortion(searchText)
    if name:
        #name = name.replace(' ','')
        # Do a name search
        if name.startswith('20'):
            results = AtlasDiffObjects.objects.filter(Q(other_designation__isnull = False) & Q(other_designation__startswith = name))
            # No results? Try the external crossmatches table.
            if len(results) == 0:
                q = TcsLatestObjectStats.objects.filter(external_crossmatches__isnull = False).filter(external_crossmatches__contains=name)
                results = list(set([x.id for x in q]))
        elif name.startswith('ATLAS'):
            results = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & Q(atlas_designation__startswith = name))
            # No results? Try the external crossmatches table.
            if len(results) == 0:
                q = TcsLatestObjectStats.objects.filter(external_crossmatches__isnull = False).filter(external_crossmatches__contains=name)
                results = list(set([x.id for x in q]))
        elif name.startswith('AT'):
            results = AtlasDiffObjects.objects.filter(Q(other_designation__isnull = False) & Q(other_designation__startswith = name.replace('AT','')))
            # No results? Try the external crossmatches table.
            if len(results) == 0:
                q = TcsLatestObjectStats.objects.filter(external_crossmatches__isnull = False).filter(external_crossmatches__contains=name)
                results = list(set([x.id for x in q]))
        elif name.startswith('SN'):
            results = AtlasDiffObjects.objects.filter(Q(other_designation__isnull = False) & Q(other_designation__startswith = name.replace('SN','')))
            # No results? Try the external crossmatches table.
            if len(results) == 0:
                q = TcsLatestObjectStats.objects.filter(external_crossmatches__isnull = False).filter(external_crossmatches__contains=name)
                results = list(set([x.id for x in q]))
        else: # name.startswith('ZTF'):
            # Check for external crossmatches.
            q = TcsLatestObjectStats.objects.filter(external_crossmatches__isnull = False).filter(external_crossmatches__contains=name)
            results = list(set([x.id for x in q]))
        #else:
        #    results = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & (Q(atlas_designation__startswith = 'ATLAS' + name) | Q(other_designation__startswith = '20' + name)))
    else:
         # It must be a coordinate or a match failure
         coords = getCoordsAndSearchRadius(searchText)
         if coords:
             searchRadius = 4.0
             if coords['radius']:
                 searchRadius = float(coords['radius'])
                 if searchRadius > 99.0:
                      searchRadius = 99.0
         
             message, xmObjects = coneSearchHTM(coords['ra'], coords['dec'], searchRadius, 'atlas_diff_objects', queryType = FULL, conn = connection, django = True)
             for xm in xmObjects:
                 dictRow = xm[1]
                 dictRow.update({'xmseparation': xm[0]})
                 # Add sexagesimal RA and Dec
                 dictRow.update({'ra_sex': ra_to_sex(dictRow['ra'])}) 
                 dictRow.update({'dec_sex': dec_to_sex(dictRow['dec'])}) 
                 if dictRow['images_id']:
                     # Get images
                     images = TcsImages.objects.get(pk=dictRow['images_id'])
                     if images:
                         dictRow.update({'images_id': images})
                 # 2018-08-07 KWS Convert the class into a dict so we can use common code elsewhere.
                 results.append(Struct(**dictRow))

    return results


def getNearbyObjectsForScatterPlot(candidate, ra, dec, coneSearchRadius = 8.0, ddc = False):
    """getNearbyObjectsForScatterPlot.

    Args:
        candidate:
        ra:
        dec:
        coneSearchRadius:
        ddc:
    """
    from django.db import connection

    recurrencePlotData = []
    recurrencePlotLabels = []
    averageObjectCoords = []
    rmsScatter = []

    xmObjects = None

    # Grab all objects within 3 arcsec of this one.
    xmList = []
    catalogueName = 'atlas_diff_objects'
    message, xmObjects = coneSearchHTM(ra, dec, coneSearchRadius, catalogueName, queryType = FULL, conn = connection, django = True)

    # The crossmatch Objects xmObjects are a list of two entry lists. The first entry in each row is the separaion.
    # The second entry is the catalogue row dictionary listing the relevant crossmatch.

    if xmObjects:
        numberOfMatches = len(xmObjects)
        # Add the objects into a list of dicts that have consistent names for all catalogues

        for xm in xmObjects:
            sys.stderr.write("\n%s\n" % str(xm))
            # Add to the list all object ids except the current one (which will have
            # a separation of zero).
            if xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]] != candidate:
                xmList.append({'xmseparation': xm[0], 'xmid': xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]})
                xmid = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]
                xmra = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][1]]
                xmdec = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][2]]
                xmName = xm[1]["atlas_designation"]
                if not xmName:
                    xmName = xmid

                xmRecurrences = []
                if ddc:
                    xmDetections = AtlasDetectionsddc.objects.filter(atlas_object_id = xmid)
                    for xmDet in xmDetections:
                        if xmDet.det != 5:
                            xmRecurrences.append({"RA": xmDet.ra, "DEC": xmDet.dec})
                    if len(xmRecurrences) == 0: 
                        xmRecurrences = []
                        for xmDet in xmDetections:
                            xmRecurrences.append({"RA": xmDet.ra, "DEC": xmDet.dec})
                else:
                    xmDetections = AtlasDiffDetections.objects.filter(atlas_object_id = xmid)
                    for xmDet in xmDetections:
                        xmRecurrences.append({"RA": xmDet.ra, "DEC": xmDet.dec})


                xmrecurrencePlotData, xmrecurrencePlotLabels, xmaverageObjectCoords, xmrmsScatter = getRecurrenceDataForPlotting(xmRecurrences, ra, dec, secRA = xmra, secDEC = xmdec, secId = xmid, secName = xmName, objectColour = 23)
                recurrencePlotData += xmrecurrencePlotData
                recurrencePlotLabels += xmrecurrencePlotLabels
                averageObjectCoords += xmaverageObjectCoords
                rmsScatter += xmrmsScatter

    recurrenceData = [recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter]
    return recurrenceData


def getNearbyObjectsFromAlternateDatabase(currentDBName, alternateDBConnections, transient, coneSearchRadius, catalogueName = 'atlas_diff_objects'):
    """getNearbyObjectsFromAlternateDatabase.

    Args:
        currentDBName:
        alternateDBConnections:
        transient:
        coneSearchRadius:
        catalogueName:
    """
    results = {}
    oldDBXmList = []

    oldDBURL = None
    try:
        # HARD WIRED OLD DATABASES DEPEND ON CURRENT DB NAME
        oldDB = alternateDBConnections[currentDBName]
        oldDBURL = oldDB[2]

        # We have to make a manual connection to the database
        try:
            conn = dbConnect(oldDB[1], 'kws', '', oldDB[0], quitOnError = False)

            message, xmObjects = coneSearchHTM(transient.ra, transient.dec, coneSearchRadius, catalogueName, queryType = FULL, conn = conn, django = False)
            conn.close()

            if xmObjects:
                for xm in xmObjects:
                    oldDBXmList.append({'xmseparation': xm[0], 'xmid': xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]], 'xmName': xm[1]["atlas_designation"], 'xmTNS': xm[1]["other_designation"], 'xmCounter': xm[1]["followup_counter"]})

        except Exception as e:
            # If for any reason we can't connect to the old database, just continue anyway
            sys.stderr.write("\n%s\n" % str(e))
            pass

    except KeyError as e:
        # If for any reason we can't find the old database in the dictionary, don't bother doing anything
        sys.stderr.write("\n%s\n" % str(e))
        pass

    xmNearestName = None
    xmNearestCounter = None

    if oldDBXmList and oldDBXmList[0]['xmName']:
        xmNearestName = oldDBXmList[0]['xmName']
        xmNearestCounter = oldDBXmList[0]['xmCounter']

    results['oldDBURL'] = oldDBURL
    results['oldDBXmList'] = oldDBXmList
    results['xmNearestName'] = xmNearestName
    results['xmNearestCounter'] = xmNearestCounter

    return results

# New code to send a message to a daemon listening on a socket.

TNS_MESSAGES = { 'SUBMIT': 'Submit',
                 'SUBMITTEST': 'SubmitTest',
                 'RESULTS': 'Results' }

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
    # When we're querying for atlas_diff_objects we probably have lots of
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
        queryFilter[prefix + rbPixParameter] = rbPix


    # 2022-01-28 KWS Added ra and dec
    ra = None
    raParameter = 'ra'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        raParameter = 'ra' + suffix
        ra = request.GET.get(raParameter)
        if ra is not None:
            break

    try:
        ra = float(ra)
    except ValueError as e:
        ra = None
    except TypeError as e:
        ra = None

    if ra:
        queryFilter[prefix + raParameter] = ra

    dec = None
    decParameter = 'dec'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        decParameter = 'dec' + suffix
        dec = request.GET.get(decParameter)
        if dec is not None:
            break

    try:
        dec = float(dec)
    except ValueError as e:
        dec = None
    except TypeError as e:
        dec = None

    if dec:
        queryFilter[prefix + decParameter] = dec


    # 2021-11-19 KWS Added realbogus_factor
    realBogus = None
    realBogusParameter = 'realbogus_factor'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        realBogusParameter = 'realbogus_factor' + suffix
        realBogus = request.GET.get(realBogusParameter)
        if realBogus is not None:
            break

    try:
        realBogus = float(realBogus)
    except ValueError as e:
        realBogus = None
    except TypeError as e:
        realBogus = None

    if realBogus:
        queryFilter[prefix + realBogusParameter] = realBogus


    otherDesignation = None
    otherDesignationParameter = 'other_designation'
    for suffix in ['__startswith', '__endswith', '']:
        otherDesignationParameter = 'other_designation' + suffix
        otherDesignation = request.GET.get(otherDesignationParameter)
        if otherDesignation is not None:
            break

    if otherDesignation:
        queryFilter[prefix + otherDesignationParameter] = otherDesignation

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

    return queryFilter


# 2023-06-22 KWS Added helper to get GW event parameters
def filterGetGWParameters(request, queryFilter, prefix = ''):
    """filterGetParameters.

    Args:
        request:
        queryFilter:
        prefix:
    """


    gwEvent = None
    gwEventParameter = 'gravity_event_id'

    gwEvent = request.GET.get('gwevent')

    if gwEvent:
        queryFilter[prefix + gwEventParameter + '__contains'] = gwEvent


    enclosingContour = None
    enclosingContourParameter = 'enclosing_contour'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        enclosingContourParameter = 'enclosing_contour' + suffix
        enclosingContour = request.GET.get(enclosingContourParameter)
        if enclosingContour is not None:
            break

    try:
        enclosingContour = float(enclosingContour)
    except ValueError as e:
        enclosingContour = None
    except TypeError as e:
        enclosingContour = None

    if enclosingContour:
        queryFilter[prefix + enclosingContourParameter] = enclosingContour

    daysSinceEvent = None
    daysSinceEventParameter = 'days_since_event'
    for suffix in ['__lt', '__lte', '__gt', '__gte', '']:
        daysSinceEventParameter = 'days_since_event' + suffix
        daysSinceEvent = request.GET.get(daysSinceEventParameter)
        if daysSinceEvent is not None:
            break

    try:
        daysSinceEvent = float(daysSinceEvent)
    except ValueError as e:
        daysSinceEvent = None
    except TypeError as e:
        daysSinceEvent = None

    if daysSinceEvent:
        queryFilter[prefix + daysSinceEventParameter] = daysSinceEvent

    return queryFilter



def getDjangoTables2ImageTemplate(imageType):
    IMAGE_TEMPLATE = """<img id="stampimages" src="{{ MEDIA_URL }}images/data/{{ dbname }}/{{ record.images_id.whole_mjd }}/{{ record.images_id.%s }}.jpeg" alt="triplet" title="{{ record.images_id.pss_filename }}" onerror="this.src='{{ STATIC_URL }}images/image_not_available.jpeg';" height="200" />""" % imageType
    return IMAGE_TEMPLATE

