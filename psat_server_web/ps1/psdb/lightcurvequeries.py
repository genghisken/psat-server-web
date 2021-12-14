# 2012-07-18 KWS This file contains all the relevant custom queries needed to build lightcurves using 'flot'.
#                They are created as custom queries for SPEED. It is also necessary to build new custom
#                objects in dbviews. Note that the code in this file relies on Django objects.  Other
#                code has been abstracted out to commonqueries so that it can be called by external scripts.

# 2012-09-26 KWS Add numpy so we can do some simple max/min calculations on the lightcurve data
import numpy as n
from .commonqueries import *

GRIZY_COLOURS = {"g": 0, "r": 1, "i": 2, "z": 3, "y": 4, "w": 5, "x": 6, "B": 7, "V": 8}

# 2017-04-07 KWS A bug has been introduced into IPP meaning that sometimes we get
#                null values for magerr.  Let's decide how to present the null
#                values.  In this case, arbitrarily choose a large magerr.

NULL_MAGERR = 0.5

def getColourPlotData(g, r, i, z, y):
    """Collect the colour info from input filter data for plotting"""
    from gkutils.commonutils import getColour, getColourStats
    import json

    colourPlotLimits = {}
    coloursJSON = []

    grColour = []
    riColour = []
    izColour = []
    colourPlotLabels = [{'label': 'g-r', 'color': 0, 'display': True},
                        {'label': 'r-i', 'color': 1, 'display': True},
                        {'label': 'i-z', 'color': 2, 'display': True}]
    meangr = None
    meanri = None
    meaniz = None

    grEvolution = None
    riEvolution = None
    izEvolution = None

    if g and r:
        grColour = getColour(g, r, FILTER_RECURRENCE_PERIOD_GR)
        if grColour and len(grColour) > 1:
            meangr, grEvolution = getColourStats(grColour)
            colourPlotLabels[0]["label"] += (' (avg = %4.2f mag,' % meangr) + (' trend = %5.3f mag/d)' % grEvolution)
    if r and i:
        riColour = getColour(r, i, FILTER_RECURRENCE_PERIOD_RI)
        if riColour and len(riColour) > 1:
            meanri, riEvolution = getColourStats(riColour)
            colourPlotLabels[1]["label"] += (' (avg = %4.2f mag,' % meanri) + (' trend = %5.3f mag/d)' % riEvolution)
    if i and z:
        izColour = getColour(i, z, FILTER_RECURRENCE_PERIOD_IZ)
        if izColour and len(izColour) > 1:
            meaniz, izEvolution = getColourStats(izColour)
            colourPlotLabels[2]["label"] += (' (avg = %4.2f mag,' % meaniz) + (' trend = %5.3f mag/d)' % izEvolution)

    xMin, xMax, yMin, yMax = getLimitsFromLCData([grColour, riColour, izColour])
    colourPlotLimits["xmin"] = xMin
    colourPlotLimits["xmax"] = xMax
    colourPlotLimits["ymin"] = yMin
    colourPlotLimits["ymax"] = yMax
    colours = [grColour, riColour, izColour]
    colourPlotLabelsJSON = [json.dumps(colourPlotLabels[0]), json.dumps(colourPlotLabels[1]), json.dumps(colourPlotLabels[2])]

    return colours, colourPlotLimits, colourPlotLabelsJSON


def getAllLCData(candidate, applyFudge = True, getColours = True, conn = None, getFollowupData = False, limits = LIMITS):
    """getAllLCData.

    Args:
        candidate:
        applyFudge:
        getColours:
        conn:
        getFollowupData:
        limits:
    """

    # 2012-07-18 KWS Add in custom queries to get lightcurve data.
    # 2013-02-12 KWS Added conn object, so that we can grab a remote database lightcurve.

    # 2014-07-09 KWS This code is a bit of a mess.  We need to make it more filter agnostic.
    #                In the meantime, to get it to work quickly, I've just added any new
    #                filters to the original list (currently grizywxBV).  We can have up to
    #                20 filters before I need to alter the lightcurve code.  The LAST value
    #                in the list is always the combined data, so ALWAYS refer to it by index
    #                of -1.

    import json
    from gkutils.commonutils import getCurrentMJD
    import sys

    # NOTE: At this point we have the data for ALL filters in the 6th row of lcData.
    #       We can use this to set the max/min limits in x (and y) if necessary.
    #       The javascript code is currently not using them, but it should. We should
    #       have checkboxes for whole survey lifetime, detection limits, etc...
    #       We just have to decide how to send the max/min data to the lightcurve code.
    #       Probably need a new varable so we don't get confused.

    # Data is currently [g, r, i, z, y, w, x, B, V, all]

    dataList = []

    # 2013-02-03 KWS Dynamically set the django raw query object here instead of in the query code.
    #                This makes the query code portable to non django MySQL queries.

    from .dbviews import CustomLCPoints, CustomFollowupLCData

    lcData = getLightcurvePoints(candidate, applyFudge = applyFudge, djangoRawObject = CustomLCPoints, conn = conn)

    if lcData and lcData[-1]:
        dataList.append(lcData[-1])
    #lcPointsJSON = [json.dumps(lcData[0]), json.dumps(lcData[1]), json.dumps(lcData[2]), json.dumps(lcData[3]), json.dumps(lcData[4]), json.dumps(lcData[5])]

    # 2017-04-07 KWS A bug has been introduced into IPP meaning that sometimes we get
    #                null values for magerr. We do NOT want to alter the
    #                getLightcurvePoints code - just the code that presents the data.

    # 2017-04-07 KWS Replace the null magerr values.

    for filterLC in lcData:
        if filterLC:
            for lc in filterLC:
                if len(lc) == 3:
                    if lc[2] is None:
                        lc[2] = NULL_MAGERR

    # For the colour plots (later) list the griz data separately
    g = lcData[0]
    r = lcData[1]
    i = lcData[2]
    z = lcData[3]
    y = lcData[4]
    w = lcData[5]
    x = lcData[6]
    B = lcData[7]
    V = lcData[8]

    lcPointsJSON = [json.dumps(g), json.dumps(r), json.dumps(i), json.dumps(z), json.dumps(y), json.dumps(w), json.dumps(x), json.dumps(B), json.dumps(V)]

    grizyArray = n.array(lcData[-1])
    discoveryDate = n.min(grizyArray[:,0])

    lcData = getLightcurveBlanks(candidate, djangoRawObject = CustomLCPoints, limits = limits)
    if lcData and lcData[-1]:
        dataList.append(lcData[-1])

    gblank = lcData[0]
    rblank = lcData[1]
    iblank = lcData[2]
    zblank = lcData[3]
    yblank = lcData[4]
    wblank = lcData[5]
    xblank = lcData[6]
    Bblank = lcData[7]
    Vblank = lcData[8]

    #lcBlanksJSON = [json.dumps(lcData[0]), json.dumps(lcData[1]), json.dumps(lcData[2]), json.dumps(lcData[3]), json.dumps(lcData[4]), json.dumps(lcData[5])]
    lcBlanksJSON = [json.dumps(lcData[0]), json.dumps(lcData[1]), json.dumps(lcData[2]), json.dumps(lcData[3]), json.dumps(lcData[4]), json.dumps(lcData[5]), json.dumps(lcData[6]), json.dumps(lcData[7]), json.dumps(lcData[8])]

    lcData = getLightcurveNonDetections(candidate, djangoRawObject = CustomLCPoints, limits = limits)
    if lcData and lcData[-1]:
        dataList.append(lcData[-1])

    gnon = lcData[0]
    rnon = lcData[1]
    inon = lcData[2]
    znon = lcData[3]
    ynon = lcData[4]
    wnon = lcData[5]
    xnon = lcData[6]
    Bnon = lcData[7]
    Vnon = lcData[8]

    #lcNonDetectionsJSON = [json.dumps(lcData[0]), json.dumps(lcData[1]), json.dumps(lcData[2]), json.dumps(lcData[3]), json.dumps(lcData[4]), json.dumps(lcData[5])]
    lcNonDetectionsJSON = [json.dumps(lcData[0]), json.dumps(lcData[1]), json.dumps(lcData[2]), json.dumps(lcData[3]), json.dumps(lcData[4]), json.dumps(lcData[5]), json.dumps(lcData[6]), json.dumps(lcData[7]), json.dumps(lcData[8])]

    # plotLabels MUST be the same length as the max number of series plotted.  In this case, there should be number_of_filters
    # x 3 data series.  Additionally plotLabels also defines the colour of each series.  Why is this done? So that we can append
    # other lightcurves from followup photometry tables (e.g. Liverpool Telescope photometry).  The data is used directly by
    # javascript so it needs to be in json format.

    # 2014-07-09 KWS Added bool(list) as the value of the display parameter.  This means only labels for lists that actually
    #                exist will get displayed.  Need also to pick out the non-detections.

    plotLabels = [json.dumps({'label':'g', 'color': 0, 'display': bool(g) or bool(gblank) or bool(gnon)}),
                  json.dumps({'label':'r', 'color': 1, 'display': bool(r) or bool(rblank) or bool(rnon)}),
                  json.dumps({'label':'i', 'color': 2, 'display': bool(i) or bool(iblank) or bool(inon)}),
                  json.dumps({'label':'z', 'color': 3, 'display': bool(z) or bool(zblank) or bool(znon)}),
                  json.dumps({'label':'y', 'color': 4, 'display': bool(y) or bool(yblank) or bool(ynon)}),
                  json.dumps({'label':'w', 'color': 5, 'display': bool(w) or bool(wblank) or bool(wnon)}),
                  json.dumps({'label':'x', 'color': 6, 'display': bool(x) or bool(xblank) or bool(xnon)}),
                  json.dumps({'label':'B', 'color': 7, 'display': bool(B) or bool(Bblank) or bool(Bnon)}),
                  json.dumps({'label':'V', 'color': 8, 'display': bool(V) or bool(Vblank) or bool(Vnon)}),
                  json.dumps({'label':'g blanks', 'color': 0, 'display': False}),
                  json.dumps({'label':'r blanks', 'color': 1, 'display': False}),
                  json.dumps({'label':'i blanks', 'color': 2, 'display': False}),
                  json.dumps({'label':'z blanks', 'color': 3, 'display': False}),
                  json.dumps({'label':'y blanks', 'color': 4, 'display': False}),
                  json.dumps({'label':'w blanks', 'color': 5, 'display': False}),
                  json.dumps({'label':'x blanks', 'color': 6, 'display': False}),
                  json.dumps({'label':'B blanks', 'color': 7, 'display': False}),
                  json.dumps({'label':'V blanks', 'color': 8, 'display': False}),
                  json.dumps({'label':'g non det', 'color': 0, 'display': False}),
                  json.dumps({'label':'r non det', 'color': 1, 'display': False}),
                  json.dumps({'label':'i non det', 'color': 2, 'display': False}),
                  json.dumps({'label':'z non det', 'color': 3, 'display': False}),
                  json.dumps({'label':'y non det', 'color': 4, 'display': False}),
                  json.dumps({'label':'w non det', 'color': 5, 'display': False}),
                  json.dumps({'label':'x non det', 'color': 6, 'display': False}),
                  json.dumps({'label':'B non det', 'color': 7, 'display': False}),
                  json.dumps({'label':'V non det', 'color': 8, 'display': False})]

    followupDetectionData = []
    followupDetectionDataBlanks = []
    if getFollowupData:
        followupFilterData, followupFilterDataBlanks, followupFullList, followupFullListBlanks = getFollowupPhotometry(candidate, djangoRawObject = CustomFollowupLCData, conn = conn)
        dataList.append(followupFullList)
        dataList.append(followupFullListBlanks)
        # get all the keys, and assign labels, colours and display flag to them

        followupPlotColours = {}
        initialFollowupPlotColour = 15

        for filter, filterdata in list(followupFilterData.items()):
            if filter not in followupPlotColours:
                followupPlotColours[filter] = initialFollowupPlotColour
                initialFollowupPlotColour += 1

            plotLabels.append(json.dumps({'label':filter, 'color': followupPlotColours[filter], 'display': True}))

            followupDetectionData.append(followupFilterData[filter])

        for filter, filterdata in list(followupFilterDataBlanks.items()):
            if filter not in followupPlotColours:
                followupPlotColours[filter] = initialFollowupPlotColour
                initialFollowupPlotColour += 1

            plotLabels.append(json.dumps({'label':filter, 'color': followupPlotColours[filter], 'display': False}))

            followupDetectionDataBlanks.append(followupFilterDataBlanks[filter])


    xMin, xMax, yMin, yMax = getLimitsFromLCData(dataList)

    today = getCurrentMJD()
    plotLimits = {}
    plotLimits["xmin"] = xMin
    plotLimits["xmax"] = xMax
    plotLimits["ymin"] = yMin
    plotLimits["ymax"] = yMax
    plotLimits["discoveryDate"] = discoveryDate
    plotLimits["today"] = today

    colourPlotData = []
    colourPlotLimits = []
    colourPlotLabels = []

    if getColours:
        colourPlotData, colourPlotLimits, colourPlotLabels = getColourPlotData(g, r, i, z, y)
        sys.stderr.write('\nCOLOUR UNFORCED =')
        sys.stderr.write(str(colourPlotData))

    return lcPointsJSON, lcBlanksJSON, lcNonDetectionsJSON, followupDetectionData, followupDetectionDataBlanks, plotLabels, plotLimits, colourPlotData, colourPlotLimits, colourPlotLabels



def getForcedLCData(candidate, getColours = True, conn = None, limits = LIMITS):
    """Get Forced Photometry plot data, including colours if necessary"""

    from .dbviews import CustomForcedLCData
    import json
    from gkutils.commonutils import getCurrentMJD
    import sys

    dataList = []

    forcedDetectionData = []
    forcedDetectionDataBlanks = []
    plotLabels = []

    forcedDetectionDataFlux = []
    plotLabelsFlux = []

    forcedFilterData, forcedFilterDataBlanks, forcedFullList, forcedFullListBlanks, forcedFilterDataFlux, forcedFullListFlux = getForcedPhotometry(candidate, djangoRawObject = CustomForcedLCData, conn = conn, limits = limits)

    # If we don't get any data no point proceeding.
    if not forcedFilterData or not forcedFilterDataFlux:
        return []

    dataList.append(forcedFullList)
    dataList.append(forcedFullListBlanks)
    # get all the keys, and assign labels, colours and display flag to them

    for filter, filterdata in list(forcedFilterData.items()):
        plotLabels.append(json.dumps({'label':filter, 'color': GRIZY_COLOURS[filter], 'display': True}))
        forcedDetectionData.append(forcedFilterData[filter])

    for filter, filterdata in list(forcedFilterDataBlanks.items()):
        plotLabels.append(json.dumps({'label':filter, 'color': GRIZY_COLOURS[filter], 'display': False}))
        forcedDetectionDataBlanks.append(forcedFilterDataBlanks[filter])

    for filter, filterdata in list(forcedFilterDataFlux.items()):
        plotLabelsFlux.append(json.dumps({'label':filter, 'color': GRIZY_COLOURS[filter], 'display': True}))
        forcedDetectionDataFlux.append(forcedFilterDataFlux[filter])

    # Grab the forced phot limits and use those to set the x limits
    grizyArray = n.array(forcedFullList)
    discoveryDate = n.min(grizyArray[:,0])

    xMin, xMax, yMin, yMax = getLimitsFromLCData(dataList)

    today = getCurrentMJD()
    plotLimits = {}
    plotLimits["xmin"] = xMin
    plotLimits["xmax"] = xMax
    plotLimits["ymin"] = yMin
    plotLimits["ymax"] = yMax
    plotLimits["discoveryDate"] = discoveryDate
    plotLimits["today"] = today

    # Grab the flux limits
    grizyArray = n.array(forcedFullListFlux)
    discoveryDate = n.min(grizyArray[:,0])

    xMin, xMax, yMin, yMax = getLimitsFromLCData([forcedFullListFlux])

    fluxLimits = {}
    fluxLimits["xmin"] = xMin
    fluxLimits["xmax"] = xMax
    fluxLimits["ymin"] = yMin
    fluxLimits["ymax"] = yMax
    fluxLimits["discoveryDate"] = discoveryDate
    fluxLimits["today"] = today

    colourPlotData = []
    colourPlotLimits = []
    colourPlotLabels = []

    if getColours:
        try:
            g = forcedFilterData["g"]
        except KeyError as e:
            g = []
        try:
            r = forcedFilterData["r"]
        except KeyError as e:
            r = []
        try:
            i = forcedFilterData["i"]
        except KeyError as e:
            i = []
        try:
            z = forcedFilterData["z"]
        except KeyError as e:
            z = []
        try:
            y = forcedFilterData["y"]
        except KeyError as e:
            y = []
        
        colourPlotData, colourPlotLimits, colourPlotLabels = getColourPlotData(g, r, i, z, y)
        sys.stderr.write('\nCOLOUR FORCED =')
        sys.stderr.write(str(colourPlotData))

    return forcedDetectionData, forcedDetectionDataBlanks, plotLabels, plotLimits, forcedDetectionDataFlux, plotLabelsFlux, fluxLimits, colourPlotData, colourPlotLimits, colourPlotLabels



def getRecurrenceDataForPlotting(candidate, primRA, primDEC, secRA = None, secDEC = None, secId = None, secName = None, objectColour = 0):
    """Grab the recurrence data in JSON format for plotting with Flot"""

    from .dbviews import CustomAllObjectOcurrencesPresentation # The plain text lightcurve query
    import json, math

    recurrences, averageObjectCoords, rmsScatter = getRecurrenceData(candidate, djangoRawObject = CustomAllObjectOcurrencesPresentation)

    recurrenceData = []

    for row in recurrences:
        recurrenceData.append([(primRA - row.RA) * math.cos(math.radians(row.DEC)) * 3600.0, (primDEC - row.DEC) * -3600.0])

    # The recurrence plot data will contain:
    # * The recurrences (deltas)
    # * The primary detection
    # * The average coordinates

    # The mean coordinates are to be displayed at the origin, so just dump [0,0] as the third series

    if secRA and secDEC:
        # This is a neighbouring detection
        # 2013-08-26 KWS Flipped east-west by multiplying x by -1.
        primaryDetection = [[(primRA - secRA) * math.cos(math.radians(primDEC)) * 3600.0, (primDEC - secDEC) * -3600.0]]
        # Add an anchor tag so that we can click on the legend to go to the new object.
        # This should really be done inside the javascript itself, but it's hard to know
        # which label to add a tag to, hence it's done here.
        objectName = '<a href="../' + str(secId) + '/">' + str(secName) + '</a>'
        meanCoordsLabel = 'mean coords'
        meanCoordsDisplay = False
    else:
        primaryDetection = [[0, 0]]
        objectName = '1st detection'
        meanCoordsLabel = 'mean coords (rms = %4.2f)' % rmsScatter
        meanCoordsDisplay = True


    recurrencePlotData = [json.dumps(recurrenceData),
                          json.dumps(primaryDetection),
                          json.dumps([[(primRA - averageObjectCoords["RA"]) * math.cos(math.radians(primDEC)) * 3600.0, (primDEC - averageObjectCoords["DEC"]) * -3600.0]])]


    recurrencePlotLabels = [json.dumps({'label': 'Recurrences', 'color': objectColour, 'display': False}),
                            json.dumps({'label': objectName, 'color': objectColour+1, 'display': True}),
                            json.dumps({'label': meanCoordsLabel, 'color': objectColour+2, 'display': meanCoordsDisplay})]

    return recurrencePlotData, recurrencePlotLabels, [averageObjectCoords], [rmsScatter]
