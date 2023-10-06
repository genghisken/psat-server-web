-- 2016-02-11 KWS Very reluctantly I've had to concede that the simplest implementation
--                of left joins in Django is to create web views.  This means that the
--                initial query, like in PS1, will be slow, but subsequent queries should
--                be fast.
--                In the longer term I am working on use of django-sqlpaginator to do this
--                query using a Django raw query, but for the time being I need the ORM
--                bells and whistles.

-- 2017-10-17 KWS Added zooniverse_score and date_modified so we can order by these columns
-- 2018-07-05 KWS Now beginning to use a view in new quickview pages, so added atlas_v_followup including:
--                * images_id
--                * detection_list_id
-- 2018-08-01 KWS New views for PESSTO text file generation. Django ORM was hammering the memory
--                and also taking minutes (vs seconds for view) to run.
create or replace view atlas_v_followup0 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '0'
;


create or replace view atlas_v_followup1 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '1'
;


create or replace view atlas_v_followup2 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '2'
;


create or replace view atlas_v_followup3 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '3'
;


create or replace view atlas_v_followup4 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '4'
;


create or replace view atlas_v_followup5 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '5'
;


create or replace view atlas_v_followup6 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '6'
;


create or replace view atlas_v_followup7 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '7'
;


create or replace view atlas_v_followup8 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '8'
;



create or replace view atlas_v_followup9 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '9'
;



create or replace view atlas_v_followup10 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '10'
;



create or replace view atlas_v_followup11 as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = '11'
;



create or replace view atlas_v_followupall as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id is not null
       and detection_list_id != 0
       and detection_list_id != 4
;



create or replace view atlas_v_followup_userdefined as
    select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.local_comments,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           g.object_group_id,
           o.detection_list_id,
           o.realbogus_factor,
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms
      from atlas_diff_objects o
inner join tcs_object_groups g
        on (o.id = g.transient_object_id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
;


create or replace view atlas_v_detections_with_mjd as
    select o.id,
           o.atlas_object_id,
           o.ra,
           o.`dec`,
           o.htm16ID,
           m.expname,
           m.mjd_obs
      from atlas_diff_detections o
inner join atlas_metadata m
        on m.id = o.atlas_metadata_id
;

create or replace view atlas_v_detectionsddc_with_mjd as
    select o.id,
           o.atlas_object_id,
           o.ra,
           o.`dec`,
           o.htm16ID,
           m.obs,
           m.mjd
      from atlas_detectionsddc o
inner join atlas_metadataddc m
        on m.id = o.atlas_metadata_id
;

-- 2018-07-05 KWS Generic followup view. Does it use the correct indexes??

create or replace view atlas_v_followup as select o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
;

-- 2019-04-16 KWS Same as above, but only pull out objects that are
--                associated with a GW event. We don't know which event,
--                but the subquery to iterate through and tag them should
--                not be particularly expensive.

create or replace view atlas_v_followup_gw as select distinct o.followup_id rank,
           o.id,
           o.atlas_designation,
           o.other_designation,
           o.ra,
           o.`dec`,
           s.ra_avg,
           s.dec_avg,
           o.object_classification,
           o.sherlockClassification,
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
           o.zooniverse_score,
           o.date_modified,
           s.external_crossmatches,
           s.discovery_target,
           s.rms,
           o.htm16ID,
           o.detection_list_id,
           o.images_id
      from atlas_diff_objects o
 left join tcs_latest_object_stats s
        on (o.id = s.id)
      join tcs_gravity_event_annotations e
        on (o.id = e.transient_object_id)
     where followup_id is not null
       and e.enclosing_contour < 100
;

-- 2023-10-04 KWS Only bring back the last 30 days. Without this restriction the query
--                returns 2.4 million rows, which takes forever to render inside Django!
--                Note that only recurrences of objects flagged within the specified
--                number of days will get reported. Old objects retrospectively promoted
--                will be missing their recurrence data.
create or replace view atlas_v_recurrencesddc_pessto as
    select o.followup_id rank,
           o.id,
           o.atlas_designation name,
           o.other_designation tns_name,
           d.ra,
           d.`dec`,
           m.obs expname,
           d.mag,
           d.dmag dm,
           m.filt filter,
           m.mjd
      from atlas_diff_objects o, atlas_detectionsddc d, atlas_metadataddc m
     where o.id = d.atlas_object_id
       and d.atlas_metadata_id = m.id
       and (o.detection_list_id = 1 or o.detection_list_id = 2)
       and o.atlas_designation is not null
       and followup_flag_date >= (now() - INTERVAL 30 DAY)
;
