# 2012-07-18 KWS Pure raw SQL code that can be shared across scripts and web apps.
#                The downside is that there is a security risk with this kind of
#                query (SQL injection attack).  However, I got fed up of writing
#                the same query again and again.

#                DO NOT IMPORT ANY DJANGO CODE IN HERE!! Any required Django objects
#                should be passed in by the calling code (e.g. djangoRawObject).

# Detection limits for drawing non-detection arrows on plots.
GLIMIT = 23.6
RLIMIT = 23.6
ILIMIT = 23.6
ZLIMIT = 22.6
YLIMIT = 21.3

# Add new limits for other filters - e.g. w and V.

LIMITS = {"g": GLIMIT,
          "r": RLIMIT,
          "i": ILIMIT,
          "z": ZLIMIT,
          "y": YLIMIT}

# Thresholds for doing PS1 colour plots.
FILTER_RECURRENCE_PERIOD = 0.5 # i.e. 1 day
FILTER_RECURRENCE_PERIOD_GR = 0.5
FILTER_RECURRENCE_PERIOD_RI = 2.0
FILTER_RECURRENCE_PERIOD_IZ = 2.0

# Pure raw text queries.  Note that if used by Django, there must be an associated model
# created in dbviews. The model is passed in as a parameter if required.

# The following 14 filters include PS1 and ATLAS filters
# 2018-11-05 KWS Added the t = tomato filter.
FILTERS = "grizywxBVRIcoht"


LC_POINTS_QUERY_ATLAS = '''\
          select o.id,
                 d.ra,
                 d.`dec`,
                 d.mag,
                 m.mjd_obs mjd,
                 cast(truncate(mjd_obs,3) as char) tdate,
                 m.exptime,
                 m.filter,
                 m.zp,
                 m.expname,
                 m.filename,
                 m.input,
                 m.reference,
                 d.atlas_metadata_id,
                 d.atlas_object_id,
                 o.atlas_designation,
                 o.other_designation,
                 d.tphot_id,
                 d.x,
                 d.y,
                 d.peakval,
                 d.skyval,
                 d.peakfit,
                 d.dpeak,
                 d.skyfit,
                 d.flux,
                 d.dflux,
                 d.major,
                 d.minor,
                 d.phi,
                 d.err,
                 d.chi_N,
                 abs(d.dpeak/d.peakfit) magerr
            from atlas_diff_objects o
            join atlas_diff_detections d
              on (d.atlas_object_id = o.id)
            join atlas_metadata m
              on (d.atlas_metadata_id = m.id)
           where o.id = %s
             and d.peakfit != 0
           '''

# 2015-12-10 KWS Updated query for DDT format schema.
LC_POINTS_QUERY_ATLAS_DDT = '''\
          select o.id,
                 d.ra,
                 d.`dec`,
                 d.mag,
                 m.mjd_obs mjd,
                 cast(truncate(mjd_obs,3) as char) tdate,
                 m.exptime,
                 m.filter,
                 m.zp,
                 m.expname,
                 m.filename,
                 m.input,
                 m.reference,
                 m.object pointing,
                 m.mag5sig,
                 d.atlas_metadata_id,
                 d.atlas_object_id,
                 o.atlas_designation,
                 o.other_designation,
                 d.tphot_id,
                 d.x,
                 d.y,
                 d.peakval,
                 d.skyval,
                 d.peakfit,
                 d.dpeak,
                 d.skyfit,
                 d.flux,
                 d.dflux,
                 d.major,
                 d.minor,
                 d.phi,
                 d.err,
                 d.chi_N,
                 d.dm magerr
            from atlas_diff_objects o
            join atlas_diff_detections d
              on (d.atlas_object_id = o.id)
            join atlas_metadata m
              on (d.atlas_metadata_id = m.id)
           where o.id = %s
             and d.deprecated is null
             and d.mag > 0
           '''

# 2016-03-02 KWS Changed order by mjd_obs desc to just order by mjd_obs
def filterWhereClause(filters = FILTERS):
    """filterWhereClause.

    Args:
        filters:
    """
    whereClauseList = []
    for filter in filters:
        whereClauseList.append('filter = %s')
    whereClause = ' or '.join(whereClauseList)
    orderBy = ' order by mjd_obs'

    return 'and (' + whereClause + ')' + orderBy



ATLAS_METADATA = '''
          select id,
                 mjd_obs mjd,
                 cast(truncate(mjd_obs,3) as char) tdate,
                 exptime,
                 filter,
                 zp,
                 expname,
                 filename,
                 input,
                 reference,
                 object pointing,
                 mag5sig
            from atlas_metadata
          '''

def metadataWhereClause(metadataIds):
    """metadataWhereClause.

    Args:
        metadataIds:
    """
    inClause = ','.join(['%s' for s in metadataIds])

    return 'where id in (' + inClause +') ' 



# 2017-06-16 KWS Updated query for DDC format schema.
LC_POINTS_QUERY_ATLAS_DDC = '''\
          select o.id,
                 d.ra,
                 d.`dec`,
                 d.mag,
                 m.mjd,
                 cast(truncate(mjd,3) as char) tdate,
                 m.texp exptime,
                 m.filt filter,
                 m.magzpt zp,
                 m.obs expname,
                 m.filename,
                 m.input,
                 m.reference,
                 m.obj pointing,
                 m.mag5sig,
                 d.atlas_metadata_id,
                 d.atlas_object_id,
                 o.atlas_designation,
                 o.other_designation,
                 d.det_id tphot_id,
                 d.ra,
                 d.dec,
                 d.mag,
                 d.dmag magerr,
                 d.x,
                 d.y,
                 d.major,
                 d.minor,
                 d.phi,
                 d.det,
                 d.chin,
                 d.pvr,
                 d.ptr,
                 d.pmv,
                 d.pkn,
                 d.pno,
                 d.pbn,
                 d.pcr,
                 d.pxt,
                 d.psc,
                 d.dup,
                 d.wpflx,
                 d.dflx 
            from atlas_diff_objects o
            join atlas_detectionsddc d
              on (d.atlas_object_id = o.id)
            join atlas_metadataddc m
              on (d.atlas_metadata_id = m.id)
           where o.id = %s
             and d.deprecated is null
           '''


# 2023-12-15 KWS Added MJD cut to where clause. Why bring back more data than we need??
def mjdWhereClauseddc(mjdThreshold, inequality = '>'):
    """mjdWhereClause.

    Args:
        mjdThreshold: MJD before or after which we don't want data
        inequality: >, >=, <, <= 
    """

    whereClause = ' and mjd ' + inequality + ' %f' % mjdThreshold
    return whereClause


# 2016-03-02 KWS Changed order by mjd_obs desc to just order by mjd_obs
def filterWhereClauseddc(filters = FILTERS):
    """filterWhereClauseddc.

    Args:
        filters:
    """
    whereClauseList = []
    for filter in filters:
        whereClauseList.append('filt = %s')
    whereClause = ' or '.join(whereClauseList)
    orderBy = ' order by mjd'

    return 'and (' + whereClause + ')' + orderBy


ATLAS_METADATADDC = '''
          select id,
                 mjd,
                 cast(truncate(mjd,3) as char) tdate,
                 texp exptime,
                 filt filter,
                 magzpt zp,
                 obs expname,
                 filename,
                 input,
                 reference,
                 obj pointing,
                 mag5sig
            from atlas_metadataddc
          '''


# We want to make this query generic, so create as many series as we have Telescopes + Instruments + Filters
# Each telescope name, instrument name and filter is regarded as a separate group for plotting and colour calculations.
# The query extracts ALL data, both LC points and Limits.  The code afterwards will group the series by filter
# ensuring that limits are also represented in the same colour.
FOLLOWUP_PHOTOMETRY_QUERY = """\
          select p.id, p.transient_object_id, p.mjd, p.mag, p.magerr, p.filter, t.name telescope_name, t.description telescope_description, i.name instrument_name, i.description instrument_description
            from tcs_followup_photometry p, tcs_followup_telescopes t, tcs_followup_telescope_instruments i
           where p.telescope_instrument_id = i.id
             and i.telescope_id = t.id
             and p.transient_object_id = %s
        order by telescope_name, instrument_name, p.filter, p.mjd
      """

# Get forced photometry only if the flux s/n ratio > 3 and limit to a minimum MJD.
FORCED_PHOTOMETRY_QUERY = """\
          select id, transient_object_id, mjd_obs, ra_psf, dec_psf, skycell, exptime, psf_inst_mag, psf_inst_mag_sig, cal_psf_mag, psf_inst_flux, psf_inst_flux_sig, filter, zero_pt
            from tcs_forced_photometry
           where transient_object_id = %s
             and mjd_obs > %s
             and psf_inst_flux_sig > 0
             and abs(psf_inst_flux / psf_inst_flux_sig) > 0.0
        order by filter, mjd_obs
      """

# Django just can't do left-joins easily, so we have to hand craft this.
FOLLOWUP_LIST_QUERY = """\
    select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           o.object_classification,
           o.followup_flag_date,
           o.observation_status,
           o.current_trend,
           s.earliest_mjd,
           s.earliest_mag,
           s.earliest_filter,
           s.latest_mjd,
           s.latest_mag,
           s.latest_filter,
           s.catalogue,
           s.catalogue_object_id,
           s.separation,
           o.realbogus_factor,
           s.external_crossmatches,
           s.discovery_target
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = %s
      """


def followupListQuery(listId, djangoRawObject = None, conn = None):
   """followupListQuery.

   Args:
       listId:
       djangoRawObject:
       conn:
   """
   from gkutils.commonutils import Struct

   resultset = []

   if djangoRawObject:
      # Assume a Django query by default
      resultset = djangoRawObject.objects.raw(FOLLOWUP_LIST_QUERY, [listId])
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (FOLLOWUP_LIST_QUERY, [listId])
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  resultset.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   return resultset



# In this query, we'll extract each plotting series and their labels in one go.
def followupPhotometryQuery(candidate, djangoRawObject = None, conn = None):
   """followupPhotometryQuery.

   Args:
       candidate:
       djangoRawObject:
       conn:
   """
   from gkutils.commonutils import Struct

   resultset = []

   if djangoRawObject:
      # Assume a Django query by default
      resultset = djangoRawObject.objects.raw(FOLLOWUP_PHOTOMETRY_QUERY, [candidate])
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (FOLLOWUP_PHOTOMETRY_QUERY, [candidate])
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  resultset.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   return resultset



def getFollowupPhotometry(candidate, djangoRawObject = None, conn = None):
    """Use the query followupPhotometryQuery but organise the data for plotting"""

    # We need to create a dictionary of filters which contain arrays of the data.
    # It's messy to do this from scratch, so defaultdict to the rescue...
    from collections import defaultdict

    recurrences = followupPhotometryQuery(candidate, djangoRawObject = djangoRawObject, conn = conn)

    # Each set of data is returned ordered by telescope, filter, mjd.  So should be easy to create new
    # points arrays.

    fullList = []
    fullListBlanks = []

    # We'll make the filter data a dictionary. The keys will also serve as the point labels.
    filterData = defaultdict(list)
    filterDataBlanks = defaultdict(list)


    for row in recurrences:
        # For the full list, we don't care about which filter or telescope the data came from
        if row.magerr:
            fullList.append([row.mjd, row.mag, row.magerr])
            filterData[row.telescope_name + ' ' + row.filter].append([row.mjd, row.mag, row.magerr])

        # Blank errors mean that this is a limit observation.  This criterion may change in the
        # future, so we'll need to be prepared to alter the code.
        if not row.magerr:
            fullListBlanks.append([row.mjd, row.mag])
            filterDataBlanks[row.telescope_name + ' ' + row.filter].append([row.mjd, row.mag])
 
    # The fullList and fullList blanks data is purely there to allow us to constrain x and y limits
    return filterData, filterDataBlanks, fullList, fullListBlanks


def forcedPhotometryQuery(candidate, djangoRawObject = None, conn = None):
   """This method exists to allow extraction of all the column data for display as raw data"""
   from gkutils.commonutils import Struct

   mjdLimit = 0.0
   resultset = []

   if djangoRawObject:
      # Assume a Django query by default
      resultset = djangoRawObject.objects.raw(FORCED_PHOTOMETRY_QUERY, [candidate, mjdLimit])
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (FORCED_PHOTOMETRY_QUERY, [candidate, mjdLimit])
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  resultset.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   return resultset


def getForcedPhotometry(candidate, djangoRawObject = None, conn = None, limits = LIMITS):
    """Use the query forcedPhotometryQuery but organise the data for plotting.
       Grab all the flux data while we're at it, so we can do both mags and flux."""

    from collections import defaultdict

    recurrences = forcedPhotometryQuery(candidate, djangoRawObject = djangoRawObject, conn = conn)

    fullList = []
    fullListBlanks = []
    fullListFlux = []

    # We'll make the filter data a dictionary. The keys will also serve as the point labels.
    filterData = defaultdict(list)
    filterDataFlux = defaultdict(list)
    filterDataBlanks = defaultdict(list)


    for row in recurrences:
        fullListFlux.append([row.mjd_obs, row.psf_inst_flux, row.psf_inst_flux_sig])
        filterDataFlux[row.filter].append([row.mjd_obs, row.psf_inst_flux, row.psf_inst_flux_sig])

        # Arbitrarily cut off the cal_psf_mag at 5.0.  Anything brighter than about 10 is likely to be garbage.
        if row.psf_inst_mag_sig and row.cal_psf_mag and row.cal_psf_mag >= 5.0:
            fullList.append([row.mjd_obs, row.cal_psf_mag, row.psf_inst_mag_sig])
            filterData[row.filter].append([row.mjd_obs, row.cal_psf_mag, row.psf_inst_mag_sig])

        # At the moment we don't pick up the forced blanks, but we'll leave this code in
        # for the time being.  We may modify the query in future to feed the blanks.
        if not row.psf_inst_mag_sig or not row.cal_psf_mag or row.cal_psf_mag < 5.0:
            fullListBlanks.append([row.mjd_obs, limits[row.filter]])
            filterDataBlanks[row.filter].append([row.mjd_obs, limits[row.filter]])

    # The fullList and fullList blanks data is purely there to allow us to constrain x and y limits
    return filterData, filterDataBlanks, fullList, fullListBlanks, filterDataFlux, fullListFlux



def lightcurvePlainQuery(candidate, mjdLimit = 55347.0, djangoRawObject = None, conn = None):
   """lightcurvePlainQuery.

   Args:
       candidate:
       mjdLimit:
       djangoRawObject:
       conn:
   """
   from gkutils.commonutils import Struct

   recurrences = []

   if djangoRawObject:
      # Assume a Django query by default
      recurrences = djangoRawObject.objects.raw(LC_PLAIN_TEXT_QUERY, [candidate, mjdLimit, candidate, mjdLimit])
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (LC_PLAIN_TEXT_QUERY, [candidate, mjdLimit, candidate, mjdLimit])
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  recurrences.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   return recurrences


# 2015-10-13 KWS Plain text forced photometry query
def lightcurveForcedPlainQuery(candidate, mjdLimit = 55347.0, djangoRawObject = None, conn = None):
   """lightcurveForcedPlainQuery.

   Args:
       candidate:
       mjdLimit:
       djangoRawObject:
       conn:
   """
   from gkutils.commonutils import Struct

   recurrences = []

   if djangoRawObject:
      # Assume a Django query by default
      recurrences = djangoRawObject.objects.raw(FORCED_PHOTOMETRY_QUERY, [candidate, mjdLimit])
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (FORCED_PHOTOMETRY_QUERY, [candidate, mjdLimit])
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  recurrences.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   return recurrences


# 2013-02-03 KWS Make the query code generic. Pass in the Django object if Django, or the
#                connection object if a standard MySQL query.
# 2015-11-26 KWS Complete rewritten this code to take variable list.  It still dumbly returns
#                a list of filters in positions defined by FILTERS.  In future we'll return a
#                dictionary or class.
def getLightcurvePoints(candidate, filters=FILTERS, lcQuery=LC_POINTS_QUERY_ATLAS_DDT + filterWhereClause(FILTERS), djangoRawObject = None, conn = None):
   """Return mjd, mag, dmag for each filter"""

   # We should return a DICTIONARY or CLASS, not a list of filters.

   from gkutils.commonutils import Struct

   recurrences = []

   if djangoRawObject:
      # Assume a Django query by default
      recurrences = djangoRawObject.objects.raw(lcQuery, tuple([candidate] + [f for f in filters]))
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (lcQuery, tuple([candidate] + [f for f in filters]))
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  recurrences.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   filtersList = []

   # Create a bunch of empty lists for each filter
   for f in FILTERS:
      exec("%s = []" % f)
      exec("%s = []" % ('n' + f))

   fullList = []

   # 2018-10-04 KWS Only plot recurrences with dup >= 0
   #                unless there are none! There must always
   #                be at least one recurrence!
   cleanedRecurrences = []
   for row in recurrences:
      if row.dup >= 0:
          cleanedRecurrences.append(row)

   if len(cleanedRecurrences) > 0:
      recurrences = cleanedRecurrences

   for row in recurrences:
      fullList.append([row.mjd, abs(row.mag), row.magerr])

      if row.filter in FILTERS:
         if row.mag >= 0:
             eval(row.filter).append([row.mjd, row.mag, row.magerr])
         else:
             eval(('n' + row.filter)).append([row.mjd, abs(row.mag), row.magerr])

   for f in FILTERS:
       filtersList.append(eval(f))
   for f in FILTERS:
       filtersList.append(eval(('n' + f)))

   filtersList.append(fullList)

   return filtersList, recurrences


# 2023-12-19 KWS Complete rewrite of the above code, which has become too complicated for the API
def getLightcurvePointsDDCAPI(candidate, filters=FILTERS, lcQuery=LC_POINTS_QUERY_ATLAS_DDC + filterWhereClauseddc(FILTERS), djangoRawObject = None, conn = None, mjdThreshold = None, inequality = '>'):

    if mjdThreshold is not None:
        lcQuery = LC_POINTS_QUERY_ATLAS_DDC + mjdWhereClauseddc(mjdThreshold, inequality = inequality) + filterWhereClauseddc(FILTERS)

    from gkutils.commonutils import Struct

    recurrences = []

    if djangoRawObject:
        # Assume a Django query by default
        recurrences = djangoRawObject.objects.raw(lcQuery, tuple([candidate] + [f for f in filters]))
    elif conn:
        # Otherwise try a raw MySQL query if we have a connecton object
        import MySQLdb
        try:
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute (lcQuery, tuple([candidate] + [f for f in filters]))
            results = cursor.fetchall ()
            cursor.close ()
            if results:
                for result in results:
                    recurrences.append(Struct(**result))

        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return []
    else:
        return []

    return recurrences


# 2016-05-04 KWS Code to collect non-detection data. Use recurrences as selected above.
def getNonDetections(recurrences, filters = FILTERS, ndQuery=ATLAS_METADATA, catalogueName = 'atlas_diff_detections', searchRadius = 200.0, djangoRawObject = None, conn = None, tolerance = 0.0):
    """Get all the non-detections for an ATLAS object.  We do this
       by cone searching around the object and collecting the unique
       exposures. The exposures in the lightcurve are then removed
       and we now have non-detections.  This is database expensive."""

    recurrenceCoords = [{"RA": row.ra, "DEC": row.dec} for row in recurrences]
    averageObjectCoords, rmsScatter = getRecurrenceData(recurrenceCoords)
    recurrenceDetections = [r.atlas_metadata_id for r in recurrences]

    from gkutils.commonutils import coneSearchHTM, QUICK, FULL, COUNT, CAT_ID_RA_DEC_COLS, Struct

    message, xmObjects = coneSearchHTM(averageObjectCoords['RA'], averageObjectCoords['DEC'], searchRadius, catalogueName, queryType = FULL, conn = conn, django = True)
    metadataIds = []
    uniqueMetadataIds = []
    if xmObjects:
        for xm in xmObjects:
            metadataIds.append(xm[1]['atlas_metadata_id'])
        uniqueMetadataIds = list(set(metadataIds))

    # Now remove the known metadata IDs from this unique list.

    filteredMetadataIds = [x for x in uniqueMetadataIds if x not in recurrenceDetections]
    # ONLY do the query if there was something in the filteredMetadataIds

    if not filteredMetadataIds:
        print("No non-detection data")
        return [[],[],[]]

    #print "UNFILTERED METADATA = ", uniqueMetadataIds
    #print "FILTERED METADATA = ", filteredMetadataIds
    # Now get the actual data from the metadata table.  These are our non-detections.
    # This is a large query containing a lot of IN statements.  We may need to refine how this is done.
    # In very busy star fields this might break the query size limit, in which case we'd need to hit
    # the database multiple times.  We might want to check len(query) before we give it to MySQL.

    refinedNdQuery = ndQuery + metadataWhereClause(filteredMetadataIds) + filterWhereClause(FILTERS)

    #print refinedNdQuery

    blanks = []

    if djangoRawObject:
        # Assume a Django query by default
        blanks = djangoRawObject.objects.raw(refinedNdQuery, tuple(filteredMetadataIds + [f for f in filters]))
    elif conn:
        # Otherwise try a raw MySQL query if we have a connecton object
        import MySQLdb
        try:
             cursor = conn.cursor(MySQLdb.cursors.DictCursor)
             cursor.execute (refinedNdQuery, tuple(filteredMetadataIds + [f for f in filters]))
             results = cursor.fetchall ()
             cursor.close ()
             if results:
                 for result in results:
                     blanks.append(Struct(**result))

        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return [[],[],[]]
    else:
        return [[],[],[]]

    filtersList = []

    # Find the last non-detection, if it exists.
    lastNonDetection = None
    firstDetection = recurrences[0]

    # Create a bunch of empty lists for each filter
    for row in FILTERS:
        exec("%s = []" % row)

    fullList = []

    for row in blanks:
        fullList.append([row.mjd, row.mag5sig])
        if row.mjd < firstDetection.mjd - tolerance:
            # This gets set on each iteration, but if mjd >= first detection mjd then
            # this value should contain the last non-detection epoch (or nothing). 
            lastNonDetection = row

        if row.filter in FILTERS:
            eval(row.filter).append([row.mjd, row.mag5sig])

    for f in FILTERS:
        filtersList.append(eval(f))

    filtersList.append(fullList)

    return filtersList, blanks, lastNonDetection

# 2017-11-15 KWS Create a dictionary out of the filters list. This is required
#                in order to pass data to plotly (alternative to flot).
def getFiltersListAsDict(filtersList):
    """getFiltersListAsDict.

    Args:
        filtersList:
    """
    filtersDict = {}

    # The filters list is defined by FILTERS. It's just a list (sometimes empty)
    # for each filter + another list of the combined data.
    for i in range(len(FILTERS)):
        if len(filtersList[i]) > 0:
            if len(filtersList[i][0]) == 3: # we have errors
                filtersDict[FILTERS[i]] = {'mjd': [x[0] for x in filtersList[i]], 'mag': [y[1] for y in filtersList[i]], 'magerr': [e[2] for e in filtersList[i]]}
            else:
                filtersDict[FILTERS[i]] = {'mjd': [x[0] for x in filtersList[i]], 'mag': [y[1] for y in filtersList[i]]}

    # Now add the combined data
    if len(filtersList[-1][0]) == 3:
        filtersDict['all'] = {'mjd': [x[0] for x in filtersList[-1]], 'mag': [y[1] for y in filtersList[-1]], 'magerr': [e[2] for e in filtersList[-1]]}
    else:
        filtersDict['all'] = {'mjd': [x[0] for x in filtersList[-1]], 'mag': [y[1] for y in filtersList[-1]]}

    return filtersDict

# 2017-08-30 KWS New code to collect non-detection data using cone search around the
#                telescope pointing positions.  Use recurrence data to remove existing
#                recurrences.
from gkutils.commonutils import ATLAS_CONESEARCH_RADIUS

def getNonDetectionsUsingATLASFootprint(recurrences, filters = FILTERS, ndQuery=ATLAS_METADATA, catalogueName = 'atlas_metadata', filterWhereClause = filterWhereClause, searchRadius = ATLAS_CONESEARCH_RADIUS, djangoRawObject = None, conn = None, tolerance = 0.0):
    """Get all the non-detections for an ATLAS object.  We do this
       by cone searching around the object and collecting the unique
       exposures. The exposures in the lightcurve are then removed
       and we now have non-detections.  This is database expensive."""

    recurrenceCoords = [{"RA": row.ra, "DEC": row.dec} for row in recurrences]
    averageObjectCoords, rmsScatter = getRecurrenceData(recurrenceCoords)
    recurrenceDetections = [r.atlas_metadata_id for r in recurrences]

    from gkutils.commonutils import coneSearchHTM, QUICK, FULL, COUNT, CAT_ID_RA_DEC_COLS, Struct, isObjectInsideATLASFootprint

    message, xmObjects = coneSearchHTM(averageObjectCoords['RA'], averageObjectCoords['DEC'], searchRadius, catalogueName, queryType = FULL, conn = conn, django = True)
    metadataIds = []
    uniqueMetadataIds = []
    if xmObjects:
        for xm in xmObjects:
            # Eliminate exposures where the object is outside the ATLAS footprint.
            inside = isObjectInsideATLASFootprint(averageObjectCoords['RA'], averageObjectCoords['DEC'], xm[1]['ra'], xm[1]['dec'], separation = xm[0])
            if inside:
                metadataIds.append(xm[1]['id'])
        uniqueMetadataIds = list(set(metadataIds))

    # Now remove the known metadata IDs from this unique list.

    filteredMetadataIds = [x for x in uniqueMetadataIds if x not in recurrenceDetections]
    # ONLY do the query if there was something in the filteredMetadataIds

    if not filteredMetadataIds:
        print("No non-detection data")
        return [[],[],[]]

    refinedNdQuery = ndQuery + metadataWhereClause(filteredMetadataIds) + filterWhereClause(FILTERS)

    blanks = []

    if djangoRawObject:
        # Assume a Django query by default
        blanks = djangoRawObject.objects.raw(refinedNdQuery, tuple(filteredMetadataIds + [f for f in filters]))
    elif conn:
        # Otherwise try a raw MySQL query if we have a connecton object
        import MySQLdb
        try:
             cursor = conn.cursor(MySQLdb.cursors.DictCursor)
             cursor.execute (refinedNdQuery, tuple(filteredMetadataIds + [f for f in filters]))
             results = cursor.fetchall ()
             cursor.close ()
             if results:
                 for result in results:
                     blanks.append(Struct(**result))

        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return [[],[],[]]
    else:
        return [[],[],[]]

    filtersList = []

    # Find the last non-detection, if it exists.
    lastNonDetection = None
    firstDetection = recurrences[0]

    # Create a bunch of empty lists for each filter
    for row in FILTERS:
        exec("%s = []" % row)

    fullList = []

    for row in blanks:
        fullList.append([row.mjd, row.mag5sig])
        if row.mjd < firstDetection.mjd - tolerance:
            # This gets set on each iteration, but if mjd >= first detection mjd then
            # this value should contain the last non-detection epoch (or nothing). 
            lastNonDetection = row

        if row.filter in FILTERS:
            eval(row.filter).append([row.mjd, row.mag5sig])

    for f in FILTERS:
        filtersList.append(eval(f))

    filtersList.append(fullList)

    return filtersList, blanks, lastNonDetection


# 2023-12-19 KWS Rewritten in simplified form the above code for the API (DDC only).
def getNonDetectionsUsingATLASFootprintAPI(recurrences, filters = FILTERS, ndQuery=ATLAS_METADATADDC, catalogueName = 'atlas_metadataddc', filterWhereClause = filterWhereClauseddc, searchRadius = ATLAS_CONESEARCH_RADIUS, djangoRawObject = None, conn = None, tolerance = 0.0, mjdThreshold = None, inequality = '>', transient = None):
    """Get all the non-detections for an ATLAS object.  We do this
       by cone searching around the object and collecting the unique
       exposures. The exposures in the lightcurve are then removed
       and we now have non-detections.  This is database expensive."""

    # If we haven't got any recurrence data (e.g. query done with mjd threshold set),
    # we can't continue since we don't know how to set the boresight RA and Dec.
    if not recurrences and transient is None:
        return []
    elif not recurrences and transient is not None:
        averageObjectCoords = {'RA': transient.ra, 'DEC': transient.dec}
    else:
        recurrenceCoords = [{"RA": row.ra, "DEC": row.dec} for row in recurrences]
        averageObjectCoords, rmsScatter = getRecurrenceData(recurrenceCoords)


    recurrenceDetections = [r.atlas_metadata_id for r in recurrences]

    from gkutils.commonutils import coneSearchHTM, QUICK, FULL, COUNT, CAT_ID_RA_DEC_COLS, Struct, isObjectInsideATLASFootprint

    message, xmObjects = coneSearchHTM(averageObjectCoords['RA'], averageObjectCoords['DEC'], searchRadius, catalogueName, queryType = FULL, conn = conn, django = True)
    metadataIds = []
    uniqueMetadataIds = []
    if xmObjects:
        for xm in xmObjects:
            # Eliminate exposures where the object is outside the ATLAS footprint.
            inside = isObjectInsideATLASFootprint(averageObjectCoords['RA'], averageObjectCoords['DEC'], xm[1]['ra'], xm[1]['dec'], separation = xm[0])
            if inside:
                metadataIds.append(xm[1]['id'])
        uniqueMetadataIds = list(set(metadataIds))

    # Now remove the known metadata IDs from this unique list.

    filteredMetadataIds = [x for x in uniqueMetadataIds if x not in recurrenceDetections]
    # ONLY do the query if there was something in the filteredMetadataIds

    if mjdThreshold is not None:
        refinedNdQuery = ndQuery + metadataWhereClause(filteredMetadataIds) +  mjdWhereClauseddc(mjdThreshold, inequality = inequality) + filterWhereClause(FILTERS)
    else:
        refinedNdQuery = ndQuery + metadataWhereClause(filteredMetadataIds) + filterWhereClause(FILTERS)

    blanks = []

    if djangoRawObject:
        # Assume a Django query by default
        blanks = djangoRawObject.objects.raw(refinedNdQuery, tuple(filteredMetadataIds + [f for f in filters]))
    elif conn:
        # Otherwise try a raw MySQL query if we have a connecton object
        import MySQLdb
        try:
             cursor = conn.cursor(MySQLdb.cursors.DictCursor)
             cursor.execute (refinedNdQuery, tuple(filteredMetadataIds + [f for f in filters]))
             results = cursor.fetchall ()
             cursor.close ()
             if results:
                 for result in results:
                     blanks.append(Struct(**result))

        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return []
    else:
        return []

    return blanks



# 2014-11-05 KWS Flux query
def getLightcurvePointsFlux(candidate, filters=FILTERS, applyFudge = False, djangoRawObject = None, conn = None):
   """getLightcurvePointsFlux.

   Args:
       candidate:
       filters:
       applyFudge:
       djangoRawObject:
       conn:
   """

   from gkutils.commonutils import Struct

   recurrences = []

   if djangoRawObject:
      # Assume a Django query by default
      recurrences = djangoRawObject.objects.raw(LC_POINTS_FLUX_QUERY, (candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (LC_POINTS_FLUX_QUERY, (candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  recurrences.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   g = []
   r = []
   i = []
   z = []
   y = []
   w = []
   x = []
   B = []
   V = []
   fullList = []
   for row in recurrences:
      if applyFudge:
         fullList.append(applyFudgeFactor(row))
      else:
         fullList.append([row.mjd, row.flux, row.fluxerr, row.exptime, row.zero_pt])

      # 2013-09-25 KWS Reduced verbose repetative code by using eval.
      if row.filter in FILTERS:
         if applyFudge:
            eval(row.filter).append(applyFudgeFactor(row))
         else:
            eval(row.filter).append([row.mjd, row.flux, row.fluxerr, row.exptime, row.zero_pt])

   return [g, r, i, z, y, w, x, B, V, fullList]



def getLightcurveBlanks(candidate, filters=FILTERS, djangoRawObject = None, conn = None, limits = LIMITS):
   """getLightcurveBlanks.

   Args:
       candidate:
       filters:
       djangoRawObject:
       conn:
       limits:
   """

   from gkutils.commonutils import Struct

   recurrences = []

   if djangoRawObject:
      # Assume a Django query by default
      recurrences = djangoRawObject.objects.raw(LC_BLANKS_QUERY, (candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (LC_BLANKS_QUERY, (candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
          results = cursor.fetchall ()
          cursor.close ()
          if results:
              for result in results:
                  recurrences.append(Struct(**result))

      except MySQLdb.Error as e:
          print("Error %d: %s" % (e.args[0], e.args[1]))
          return []
   else:
      return []

   g = []
   r = []
   i = []
   z = []
   y = []
   w = []
   x = []
   B = []
   V = []
   fullList = []
   for row in recurrences:
      fullList.append([row.mjd])
      if row.filter in FILTERS:
         eval(row.filter).append([float(row.mjd), limits[row.filter]])

   return [g, r, i, z, y, w, x, B, V, fullList]


def getLimitsFromLCData(dataList):
    '''Get the xMax, xMin, yMax, yMin of provided data'''

    # Should probably move this into utils

    # At some stage we also want to provide a mechanism for getting
    # current MJD and current MJD - 90 days...

    import numpy as n

    # This code assumes that all the data is in the form of x, y, error.
    # The dataList elements are ususally the grizy merged array, the
    # grizy blanks and grizy non-detections.

    # If no error is provided, a zero error column will be added.

    # Want to return individual array max/mins in a list, and total max/min

    xMin = []
    yMin = []
    xMax = []
    yMax = []

    firstPass = True

    for row in dataList:

        if not row:
            continue

        dataArray = n.array(row)

        # If there's only ONE column:
        if len(row[0]) < 2:
            nans = []
            for i in range(len(row)):
                nans.append([n.nan])
            dataArray = n.column_stack((dataArray, n.array(nans)) )

        # If there's only TWO columns:
        if len(row[0]) < 3:
            dataArray = n.column_stack((dataArray, n.zeros( (len(row),1) )))

        if firstPass:
            concatArray = dataArray
        else:
            concatArray = n.vstack((dataArray, concatArray))

        firstPass = False

        xMin.append(n.nanmin(dataArray[:,0]))
        xMax.append(n.nanmax(dataArray[:,0]))
        yMin.append(n.nanmin(dataArray[:,1]))
        yMax.append(n.nanmax(dataArray[:,1]))

    if not firstPass:
        # If the code above has run, then firstPass must always be false.
        xMin.append(n.nanmin(concatArray[:,0]))
        xMax.append(n.nanmax(concatArray[:,0]))
        yMin.append(n.nanmin(concatArray[:,1]))
        yMax.append(n.nanmax(concatArray[:,1]))

    # Return 4 arrays whose length is 1+ number of input arrays.
    # The last element of each array is the min/max for the concatenated
    # arrays.

    return xMin, xMax, yMin, yMax


def colourDataPlainQuery(candidate, applyFudge = False, djangoRawObject = None, conn = None):
    """Call the previously defined queries to return plain text colour data"""

    from gkutils.commonutils import getColour, getColourStats

    # All the code to do this query is defined above, so it should be a simple matter
    # of calling that code.

    # Although we request the y-band data, we'll not bother dealing with z-y for the time being.

    lcData, recurrences = getLightcurvePoints(candidate, applyFudge = applyFudge, djangoRawObject = djangoRawObject, conn = conn)

    # For the colour plots (later) list the griz data separately
    g = lcData[0]
    r = lcData[1]
    i = lcData[2]
    z = lcData[3]
    y = lcData[4]

    grColour = []
    riColour = []
    izColour = []

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
    if r and i:
        riColour = getColour(r, i, FILTER_RECURRENCE_PERIOD_RI)
        if riColour and len(riColour) > 1:
            meanri, riEvolution = getColourStats(riColour)
    if i and z:
        izColour = getColour(i, z, FILTER_RECURRENCE_PERIOD_IZ)
        if izColour and len(izColour) > 1:
            meaniz, izEvolution = getColourStats(izColour)

    return grColour, meangr, grEvolution, riColour, meanri, riEvolution, izColour, meaniz, izEvolution


def getRecurrenceData(recurrences):
    """Get all the recurrence plotting data for dynamic recurrence plots"""

    # Create a dict of RA and DEC so that we can call the RMS function.
    # Also, pick out the designated object RA and DEC primary coords.

    from gkutils.commonutils import calculateRMSScatter

    objectCoordinateRecurrences = []
    primaryObjectCoords = {}
    averageObjectCoords = {}

    primaryDetectionFound = False

    avgRa, avgDec, rmsScatter =  calculateRMSScatter(recurrences)
    averageObjectCoords["RA"] = avgRa
    averageObjectCoords["DEC"] = avgDec

    return averageObjectCoords, rmsScatter


def main(argv = None):
    """Test harness"""
    import optparse, sys
    from gkutils.commonutils import dbConnect

    if argv is None:
        argv = sys.argv

    usage = "Usage: %s <username> <password> <database> <hostname> [<candidate>] [<candidate> ...]" % argv[0]
    if len(argv) < 5:
        sys.exit(usage)

    candidateList = []

    parser = optparse.OptionParser(usage=usage)

    parser.add_option('--ddc', default=False, action="store_true",
                      help='Use the DDC schema for queries')


    options, args = parser.parse_args()
    ddc = options.ddc

    username = args[0]
    password = args[1]
    database = args[2]
    hostname = args[3]

    if len(args) > 4:
        for i in range(4,len(args)):
            candidateList.append({'id': int(args[i])})

    conn = dbConnect(hostname, username, password, database)

    #from lightcurvequeries import getLCData

    for candidate in candidateList:
       if ddc:
           p, recurrences = getLightcurvePoints(candidate['id'], lcQuery=LC_POINTS_QUERY_ATLAS_DDC + filterWhereClauseddc(FILTERS), conn = conn)
       else:
           p, recurrences = getLightcurvePoints(candidate['id'], conn = conn)

       if ddc:
           b, blanks, lastNonDetection = getNonDetectionsUsingATLASFootprint(recurrences, conn = conn, ndQuery=ATLAS_METADATADDC, filterWhereClause = filterWhereClauseddc, catalogueName = 'atlas_metadataddc')
       else:
           b, blanks, lastNonDetection = getNonDetectionsUsingATLASFootprint(recurrences, conn = conn)
           #b, blanks, lastNonDetection = getNonDetections(recurrences, conn = conn, searchRadius=500, tolerance = 0.001)

       #print p, recurrences

       print("DETECTIONS")
       exposures = []
       print("mjd filter expname pointing mag5sig diffimage tphotfile")
       for row in recurrences:
           aux = ''
           if int(row.mjd) >= 57466:
               aux = 'AUX/'
           print(row.mjd, row.filter, row.expname, row.pointing, row.mag5sig, '/atlas/diff/02a/' + str(int(row.mjd)) + '/' + row.expname + '.diff.fz', '/atlas/red/02a/' + str(int(row.mjd)) + '/' + aux + row.expname + '.tph')
           exposures.append(row.expname)


       #print b
       print("NON-DETECTIONS")
       print("mjd filter expname pointing mag5sig diffimage tphotfile")
       for row in blanks:
           aux = ''
           if int(row.mjd) >= 57466:
               aux = 'AUX/'
           print(row.mjd, row.filter, row.expname, row.pointing, row.mag5sig, '/atlas/diff/02a/' + str(int(row.mjd)) + '/' + row.expname + '.diff.fz', '/atlas/red/02a/' + str(int(row.mjd)) + '/' + aux + row.expname + '.tph')
           exposures.append(row.expname)

       if lastNonDetection:
           print("LAST NON-DETECTION = ", lastNonDetection.mjd, lastNonDetection.filter, lastNonDetection.expname, lastNonDetection.pointing, lastNonDetection.mag5sig, lastNonDetection.exptime)

       uniqueExposures = sorted(list(set(exposures)))
       exposureList = []
       tphotList = []

       for exp in uniqueExposures:
           camera = exp[0:3]
           mjd = exp[3:8]
           diffImage = camera + '/' + mjd + '/' + exp + '.diff.fz'
           aux = ''
           if int(mjd) >= 57466:
               aux = 'AUX/'
           inputTphot = camera + '/' + mjd + '/' + aux + exp + '.tph'
           exposureList.append(diffImage)
           tphotList.append(inputTphot)


       for row in tphotList:
           print(row)

       print()

       for row in exposureList:
           print(row)
       #lcPointsJSON, plotLabelsJSON, plotLimits = getLCData(candidate['id'], conn = conn)
       #print lcPointsJSON
       #print plotLabelsJSON
       #print plotLimits

if __name__ == '__main__':
    main()
