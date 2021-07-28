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

# 2016-11-30 KWS Set COUNTS_LIMIT arbitrarily to 200 before using calculated offset
COUNTS_LIMIT = 200

# Pure raw text queries.  Note that if used by Django, there must be an associated model
# created in dbviews. The model is passed in as a parameter if required.

LC_PLAIN_TEXT_QUERY = '''\
          select o.id, o.id transient_object_id, m.imageid, m.mjd_obs, o.ra_psf, o.dec_psf, o.psf_inst_mag, o.psf_inst_mag_sig, o.ap_mag, o.cal_psf_mag, o.psf_inst_flux, o.psf_inst_flux_sig, substr(m.fpa_filter,1,1) filter, o.flags, m.filename cmf_file, i.name
            from tcs_transient_objects o
      inner join tcs_cmf_metadata m
              on (o.tcs_cmf_metadata_id = m.id)
       left join tcs_image_groups i
              on (o.image_group_id = i.id)
           where o.id = %s
             and m.mjd_obs > %s
           union all
          select r.id, r.transient_object_id, m.imageid, m.mjd_obs, r.ra_psf, r.dec_psf, r.psf_inst_mag, r.psf_inst_mag_sig, r.ap_mag, r.cal_psf_mag, r.psf_inst_flux, r.psf_inst_flux_sig, substr(m.fpa_filter,1,1) filter, r.flags, m.filename cmf_file, i.name
            from tcs_transient_reobservations r
      inner join tcs_cmf_metadata m
              on (r.tcs_cmf_metadata_id = m.id)
       left join tcs_image_groups i
              on (r.image_group_id = i.id)
           where r.transient_object_id = %s
             and m.mjd_obs > %s
        order by mjd_obs desc'''


LC_POINTS_QUERY = """\
         select id, mag, magerr, mjd, filter, exptime, inst_mag
           from (
         select o.id, o.cal_psf_mag mag, o.psf_inst_mag_sig magerr, m.mjd_obs mjd, substr(m.fpa_filter,1,1) filter, m.exptime, o.psf_inst_mag inst_mag
           from tcs_transient_objects o, tcs_cmf_metadata m
          where o.tcs_cmf_metadata_id = m.id
            and o.id = %s
            and o.cal_psf_mag is not null
         union all
         select r.transient_object_id id, r.cal_psf_mag mag, r.psf_inst_mag_sig magerr, m.mjd_obs mjd, substr(m.fpa_filter,1,1) filter, m.exptime, r.psf_inst_mag inst_mag
           from tcs_transient_reobservations r, tcs_cmf_metadata m
          where r.tcs_cmf_metadata_id = m.id
            and r.transient_object_id = %s
            and r.cal_psf_mag is not null
         ) temp
         where (filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%'))
         order by mjd
      """

# 2014-11-05 KWS Could do with above again, but this time the flux, not mags
# 2015-10-12 KWS Added zero_pt.
LC_POINTS_FLUX_QUERY = """\
         select id, flux, fluxerr, mjd, filter, exptime, inst_mag, zero_pt
           from (
         select o.id, o.psf_inst_flux flux, o.psf_inst_flux_sig fluxerr, m.mjd_obs mjd, substr(m.fpa_filter,1,1) filter, m.exptime, o.psf_inst_mag inst_mag, m.zero_pt
           from tcs_transient_objects o, tcs_cmf_metadata m
          where o.tcs_cmf_metadata_id = m.id
            and o.id = %s
            and o.cal_psf_mag is not null
         union all
         select r.transient_object_id id, r.psf_inst_flux flux, r.psf_inst_flux_sig fluxerr, m.mjd_obs mjd, substr(m.fpa_filter,1,1) filter, m.exptime, r.psf_inst_mag inst_mag, m.zero_pt
           from tcs_transient_reobservations r, tcs_cmf_metadata m
          where r.tcs_cmf_metadata_id = m.id
            and r.transient_object_id = %s
            and r.cal_psf_mag is not null
         ) temp
         where (filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%'))
         order by mjd
      """


# 2016-11-30 KWS Pull out the deteff_counts, deteff_magref, deteff_calculated_offset,
#                exptime, zero_pt values so we can plot limiting mags
LC_BLANKS_QUERY = """\
         select id, mjd, filter, deteff_counts, deteff_magref, deteff_calculated_offset, exptime, zero_pt
           from (
         select o.id, o.cal_psf_mag mag, o.psf_inst_mag_sig magerr, m.mjd_obs mjd, substr(m.fpa_filter,1,1) filter, deteff_counts, deteff_magref, deteff_calculated_offset, exptime, zero_pt
           from tcs_transient_objects o, tcs_cmf_metadata m
          where o.tcs_cmf_metadata_id = m.id
            and o.id = %s
            and o.cal_psf_mag is null
         union all
         select r.transient_object_id id, r.cal_psf_mag mag, r.psf_inst_mag_sig magerr, m.mjd_obs mjd, substr(m.fpa_filter,1,1) filter, deteff_counts, deteff_magref, deteff_calculated_offset, exptime, zero_pt
           from tcs_transient_reobservations r, tcs_cmf_metadata m
          where r.tcs_cmf_metadata_id = m.id
            and r.transient_object_id = %s
            and r.cal_psf_mag is null
         ) temp
         where (filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%') or filter like concat(%s,'%%'))
         order by mjd
      """

# 2013-07-17 KWS Corrected query below to be compatible with BOTH 3pi and MD.
# 2014-01-08 KWS Introduced the new skycell and tessellation columns into the
#                query, which vastly improves the speed.
# 2016-11-30 KWS Pull out the deteff_counts, deteff_magref, deteff_calculated_offset,
#                exptime, zero_pt values so we can plot limiting mags
LC_NON_DET_QUERY = """\
         select distinct mjd_obs mjd,
                         substr(mm.fpa_filter,1,1) filter, 1 id, deteff_counts, deteff_magref, deteff_calculated_offset, exptime, zero_pt
           from tcs_cmf_metadata mm,
           (
             select distinct field, skycell
               from (
               select
                      skycell,
                      case
                          when instr(m.tessellation,'MD') then substr(m.tessellation, instr(m.tessellation,'MD'),4)
                          when instr(m.tessellation,'RINGS') then substr(m.tessellation, instr(m.tessellation,'RINGS'),8)
                          else 'null'
                      end as field
                 from tcs_cmf_metadata m, tcs_transient_objects o
                where o.tcs_cmf_metadata_id = m.id
                  and o.id = %s
                union
               select
                      skycell,
                      case
                          when instr(m.tessellation,'MD') then substr(m.tessellation, instr(m.tessellation,'MD'),4)
                          when instr(m.tessellation,'RINGS') then substr(m.tessellation, instr(m.tessellation,'RINGS'),8)
                          else 'null'
                      end as field
                 from tcs_cmf_metadata m, tcs_transient_reobservations r
                where r.tcs_cmf_metadata_id = m.id
                  and r.transient_object_id = %s
               ) fieldandskycell
           ) det
         where mm.skycell = det.skycell
           and mm.tessellation like concat(det.field,'%%')
           and imageid not in
             (
                      select imageid
                        from (
                      select m.imageid
                        from tcs_transient_objects o, tcs_cmf_metadata m
                       where o.tcs_cmf_metadata_id = m.id
                         and o.id = %s
                         and o.cal_psf_mag is null
                      union all
                      select m.imageid
                        from tcs_transient_reobservations r, tcs_cmf_metadata m
                       where r.tcs_cmf_metadata_id = m.id
                         and r.transient_object_id = %s
                         and r.cal_psf_mag is null
                      ) temp1
             )
           and imageid not in
             (
                      select imageid
                        from (
                      select m.imageid
                        from tcs_transient_objects o, tcs_cmf_metadata m
                       where o.tcs_cmf_metadata_id = m.id
                         and o.id = %s
                         and o.cal_psf_mag is not null
                      union all
                      select m.imageid
                        from tcs_transient_reobservations r, tcs_cmf_metadata m
                       where r.tcs_cmf_metadata_id = m.id
                         and r.transient_object_id = %s
                         and r.cal_psf_mag is not null
                      ) temp2
             )
           and (fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%'))
         order by mm.mjd_obs
      """

# 2013-10-11 KWS Rehash of LC detections query based on the Non-detections query below.
#                This allows us to request stamps based on new detections whilst not
#                overwriting the existing ones.
# 2015-05-31 KWS Added filename, ppsub_input, ppsub_reference to selection.
LC_DET_QUERY = """\
         select mjd_obs mjd, substr(fpa_filter,1,1) filter, imageid, cast(truncate(mjd_obs,3) as char) tdate, ipp_idet, ra_psf, dec_psf, o.id, filename, ppsub_input, ppsub_reference, m.skycell sc,
                case
                    when instr(m.filename,'MD') then substr(m.filename, instr(m.filename,'MD'),4)
                    when instr(m.filename,'RINGS') then substr(m.filename, instr(m.filename,'RINGS'),8)
                    else 'null'
                end as field,
                case
                    -- 3pi
                    when instr(m.filename,'WS') then if(instr(m.filename,'skycell'), replace(substr(m.filename, instr(m.filename,'skycell'),instr(m.filename,'.dif') - instr(m.filename,'skycell')), '.WS', ''), 'null')
                    -- MD
                    else if(instr(m.filename,'skycell'), replace(substr(m.filename, instr(m.filename,'skycell'),instr(m.filename,'.dif') - instr(m.filename,'skycell')), '.SS', ''), 'null')
                end as skycell
           from tcs_transient_objects o, tcs_cmf_metadata m
          where o.tcs_cmf_metadata_id = m.id
            and o.id = %s
            and o.cal_psf_mag is not null
            and (fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%'))
         union all
         select mjd_obs mjd, substr(fpa_filter,1,1) filter, imageid, cast(truncate(mjd_obs,3) as char) tdate, ipp_idet, ra_psf, dec_psf, transient_object_id id, filename, ppsub_input, ppsub_reference, m.skycell sc,
                case
                    when instr(m.filename,'MD') then substr(m.filename, instr(m.filename,'MD'),4)
                    when instr(m.filename,'RINGS') then substr(m.filename, instr(m.filename,'RINGS'),8)
                    else 'null'
                end as field,
                case
                    -- 3pi
                    when instr(m.filename,'WS') then if(instr(m.filename,'skycell'), replace(substr(m.filename, instr(m.filename,'skycell'),instr(m.filename,'.dif') - instr(m.filename,'skycell')), '.WS', ''), 'null')
                    -- MD
                    else if(instr(m.filename,'skycell'), replace(substr(m.filename, instr(m.filename,'skycell'),instr(m.filename,'.dif') - instr(m.filename,'skycell')), '.SS', ''), 'null')
                end as skycell
           from tcs_transient_reobservations r, tcs_cmf_metadata m
          where r.tcs_cmf_metadata_id = m.id
            and r.transient_object_id = %s
            and r.cal_psf_mag is not null
            and (fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%'))
       order by mjd, imageid, ipp_idet
      """


# 2013-09-16 KWS Non-detections AND Blanks so that we can request postage stamps for blank areas...
# 2015-05-31 KWS Added filename, ppsub_input, ppsub_reference to selection.
LC_NON_DET_AND_BLANKS_QUERY = """\
         select distinct mjd_obs mjd, substr(mm.fpa_filter,1,1) filter, imageid, cast(truncate(mm.mjd_obs,3) as char) tdate, field, det.skycell, filename, ppsub_input, ppsub_reference, mm.skycell sc, mm.zero_pt, mm.exptime, mm.deteff_counts, mm.deteff_magref, mm.deteff_calculated_offset
           from tcs_cmf_metadata mm,
           (
             select distinct field, skycell
               from (
               select
                      skycell,
                      case
                          when instr(m.tessellation,'MD') then substr(m.tessellation, instr(m.tessellation,'MD'),4)
                          when instr(m.tessellation,'RINGS') then substr(m.tessellation, instr(m.tessellation,'RINGS'),8)
                          else 'null'
                      end as field
                 from tcs_cmf_metadata m, tcs_transient_objects o
                where o.tcs_cmf_metadata_id = m.id
                  and o.id = %s
                union
               select
                      skycell,
                      case
                          when instr(m.tessellation,'MD') then substr(m.tessellation, instr(m.tessellation,'MD'),4)
                          when instr(m.tessellation,'RINGS') then substr(m.tessellation, instr(m.tessellation,'RINGS'),8)
                          else 'null'
                      end as field
                 from tcs_cmf_metadata m, tcs_transient_reobservations r
                where r.tcs_cmf_metadata_id = m.id
                  and r.transient_object_id = %s
               ) fieldandskycell
           ) det
         where mm.skycell = det.skycell and mm.tessellation like concat(det.field,'%%')
           and imageid not in
             (
                      select imageid
                        from (
                      select m.imageid
                        from tcs_transient_objects o, tcs_cmf_metadata m
                       where o.tcs_cmf_metadata_id = m.id
                         and o.id = %s
                         and o.cal_psf_mag is not null
                      union all
                      select m.imageid
                        from tcs_transient_reobservations r, tcs_cmf_metadata m
                       where r.tcs_cmf_metadata_id = m.id
                         and r.transient_object_id = %s
                         and r.cal_psf_mag is not null
                      ) temp2
             )
           and (fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%'))
         order by mm.mjd_obs
      """


# This is a query for ATLAS detections.  We need the input image, the template image and the diff image so
# we can cut stamps out of them.

# 2014-07-08 KWS Filters can be grizywxBV, so add more OR statements accordingly.
LC_DET_QUERY_ATLAS = """\
         select mjd_obs mjd, substr(fpa_filter,1,1) filter, imageid, cast(truncate(mjd_obs,3) as char) tdate, ipp_idet, ra_psf, dec_psf, o.id, x_psf, y_psf, m.diffim, m.inputim, m.templim
           from tcs_transient_objects o, tcs_cmf_metadata m
          where o.tcs_cmf_metadata_id = m.id
            and o.id = %s
            and o.cal_psf_mag is not null
            and (fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%'))
         union all
         select mjd_obs mjd, substr(fpa_filter,1,1) filter, imageid, cast(truncate(mjd_obs,3) as char) tdate, ipp_idet, ra_psf, dec_psf, transient_object_id id, x_psf, y_psf, m.diffim, m.inputim, m.templim
           from tcs_transient_reobservations r, tcs_cmf_metadata m
          where r.tcs_cmf_metadata_id = m.id
            and r.transient_object_id = %s
            and r.cal_psf_mag is not null
            and (fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%') or fpa_filter like concat(%s,'%%'))
       order by mjd, imageid, ipp_idet
      """


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
          select id, transient_object_id, mjd_obs, ra_psf, dec_psf, skycell, exptime, psf_inst_mag, psf_inst_mag_sig, cal_psf_mag, psf_inst_flux, psf_inst_flux_sig, filter, zero_pt, fpa_id
            from tcs_forced_photometry
           where transient_object_id = %s
             and mjd_obs > %s
             and psf_inst_flux_sig > 0
             and abs(psf_inst_flux / psf_inst_flux_sig) > 0.0
        order by filter, mjd_obs
      """


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
    from gkutils.commonutils import fluxToMicroJansky

    recurrences = forcedPhotometryQuery(candidate, djangoRawObject = djangoRawObject, conn = conn)

    fullList = []
    fullListBlanks = []
    fullListFlux = []

    # We'll make the filter data a dictionary. The keys will also serve as the point labels.
    filterData = defaultdict(list)
    filterDataFlux = defaultdict(list)
    filterDataBlanks = defaultdict(list)


    for row in recurrences:
        # 2020-02-03 KWS Present the flux in microJanskys.

        fullListFlux.append([row.mjd_obs, fluxToMicroJansky(row.psf_inst_flux, row.exptime, row.zero_pt), fluxToMicroJansky(row.psf_inst_flux_sig, row.exptime, row.zero_pt)])
        filterDataFlux[row.filter].append([row.mjd_obs, fluxToMicroJansky(row.psf_inst_flux, row.exptime, row.zero_pt), fluxToMicroJansky(row.psf_inst_flux_sig, row.exptime, row.zero_pt)])

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


# 2011-08-15 KWS Added the fudge factor to be applied to old data because of cal_psf_mag issues.
# 2014-07-03 KWS Added other filters.
def applyFudgeFactor(row):
   """applyFudgeFactor.

   Args:
       row:
   """

   from math import log10

   mjd = row.mjd
   magerr = row.magerr
   mag = None

   if row.mjd > 55248.0 and row.mjd < 55260.0 and row.mag is not None and row.inst_mag is not None and abs(row.mag) > 0 and abs(row.inst_mag) > 0 and row.filter in 'grizy':
      mag = row.inst_mag+25.0+2.5*log10(row.exptime)
   elif row.mjd < 55260.0 and (row.mag == 0.0 or row.mag is None) and row.inst_mag is not None and abs(row.inst_mag) > 0 and row.filter in 'grizy':
      mag = row.inst_mag+25.0+2.5*log10(row.exptime)
   elif (row.mjd >= 55260.0 and (row.mag == 0.0 or row.mag is None) and row.inst_mag is not None and abs(row.inst_mag) > 0) or (row.mjd > 55260.0 and row.mag > 24.5 and row.inst_mag is not None and abs(row.inst_mag) > 0):
      if row.filter == 'g':
         mag = row.inst_mag+25.0+2.5*log10(row.exptime)+2*(24.58 + 2.5*log10(113) - 25 - 2.5*log10(row.exptime))
      elif row.filter == 'r':
         mag = row.inst_mag+25.0+2.5*log10(row.exptime)+2*(24.80 + 2.5*log10(113) - 25 - 2.5*log10(row.exptime))
      elif row.filter == 'i':
         mag = row.inst_mag+25.0+2.5*log10(row.exptime)+2*(24.74 + 2.5*log10(240) - 25 - 2.5*log10(row.exptime))
      elif row.filter == 'z':
         mag = row.inst_mag+25.0+2.5*log10(row.exptime)+2*(24.26 + 2.5*log10(240) - 25 - 2.5*log10(row.exptime))
      elif row.filter == 'y':
         mag = row.inst_mag+25.0+2.5*log10(row.exptime)+2*(23.41 + 2.5*log10(240) - 25 - 2.5*log10(row.exptime))
      else: # Don't do anything - particularly for any new filters
         mag = row.mag

   else:
      mag = row.mag

   return [mjd, mag, magerr]


# 2013-02-03 KWS Make the query code generic. Pass in the Django object if Django, or the
#                connection object if a standard MySQL query.
def getLightcurvePoints(candidate, filters="grizywxBV", applyFudge = False, djangoRawObject = None, conn = None):
   """getLightcurvePoints.

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
      recurrences = djangoRawObject.objects.raw(LC_POINTS_QUERY, (candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (LC_POINTS_QUERY, (candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
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
         fullList.append([row.mjd, row.mag, row.magerr])

      # 2013-09-25 KWS Reduced verbose repetative code by using eval.
      if row.filter in 'grizywxBV':
         if applyFudge:
            eval(row.filter).append(applyFudgeFactor(row))
         else:
            eval(row.filter).append([row.mjd, row.mag, row.magerr])

   return [g, r, i, z, y, w, x, B, V, fullList]

# 2014-11-05 KWS Flux query
def getLightcurvePointsFlux(candidate, filters="grizywxBV", applyFudge = False, djangoRawObject = None, conn = None):
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
      if row.filter in 'grizywxBV':
         if applyFudge:
            eval(row.filter).append(applyFudgeFactor(row))
         else:
            eval(row.filter).append([row.mjd, row.flux, row.fluxerr, row.exptime, row.zero_pt])

   return [g, r, i, z, y, w, x, B, V, fullList]



def getLightcurveBlanks(candidate, filters="grizywxBV", djangoRawObject = None, conn = None, limits = LIMITS):
   """getLightcurveBlanks.

   Args:
       candidate:
       filters:
       djangoRawObject:
       conn:
       limits:
   """

   from gkutils.commonutils import Struct
   from math import log10

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
      if row.filter in 'grizywxBV':
         if row.deteff_magref is None or row.deteff_counts is None or row.deteff_calculated_offset is None:
            eval(row.filter).append([float(row.mjd), limits[row.filter]])
         else:
            if int(row.deteff_counts) < COUNTS_LIMIT:
               detectionLimit = float(row.deteff_magref) + 2.5 * log10(row.exptime) + float(row.zero_pt)
            else:
               detectionLimit = float(row.deteff_magref) + 2.5 * log10(row.exptime) + float(row.zero_pt) + float(row.deteff_calculated_offset)
            eval(row.filter).append([float(row.mjd), detectionLimit])

   return [g, r, i, z, y, w, x, B, V, fullList]

def getLightcurveNonDetections(candidate, filters="grizywxBV", djangoRawObject = None, conn = None, limits = LIMITS):
   """getLightcurveNonDetections.

   Args:
       candidate:
       filters:
       djangoRawObject:
       conn:
       limits:
   """

   from gkutils.commonutils import Struct
   from math import log10

   recurrences = []

   if djangoRawObject:
      # Assume a Django query by default
      recurrences = djangoRawObject.objects.raw(LC_NON_DET_QUERY, (candidate, candidate, candidate, candidate, candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
   elif conn:
      # Otherwise try a raw MySQL query if we have a connecton object
      import MySQLdb
      try:
          cursor = conn.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute (LC_NON_DET_QUERY, (candidate, candidate, candidate, candidate, candidate, candidate, filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], filters[6], filters[7], filters[8]))
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
      fullList.append([float(row.mjd)])
      if row.filter in 'grizywxBV':
         if row.deteff_magref is None or row.deteff_counts is None or row.deteff_calculated_offset is None:
            eval(row.filter).append([float(row.mjd), limits[row.filter]])
         else:
            if int(row.deteff_counts) < COUNTS_LIMIT:
               detectionLimit = float(row.deteff_magref) + 2.5 * log10(row.exptime) + float(row.zero_pt)
            else:
               detectionLimit = float(row.deteff_magref) + 2.5 * log10(row.exptime) + float(row.zero_pt) + float(row.deteff_calculated_offset)
            eval(row.filter).append([float(row.mjd), detectionLimit])

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

    lcData = getLightcurvePoints(candidate, applyFudge = applyFudge, djangoRawObject = djangoRawObject, conn = conn)

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


def getRecurrenceData(candidate, djangoRawObject = None, conn = None):
    """Get all the recurrence plotting data for dynamic recurrence plots"""

    # Create a dict of RA and DEC so that we can call the RMS function.
    # Also, pick out the designated object RA and DEC primary coords.

    from gkutils.commonutils import calculateRMSScatter

    recurrences = lightcurvePlainQuery(candidate, mjdLimit = 0, djangoRawObject = djangoRawObject, conn = conn)

    objectCoordinateRecurrences = []
    primaryObjectCoords = {}
    averageObjectCoords = {}

    primaryDetectionFound = False

    for row in recurrences:
        objectCoordinateRecurrences.append({"RA": row.RA, "DEC": row.DEC})

    avgRa, avgDec, rmsScatter =  calculateRMSScatter(objectCoordinateRecurrences)
    averageObjectCoords["RA"] = avgRa
    averageObjectCoords["DEC"] = avgDec

    return recurrences, averageObjectCoords, rmsScatter

