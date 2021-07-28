-- Recurrent Objects --
create or replace view psdb_web_v_recurrent_objects_presentation as
--     select o.id, o.id as transient_object_id, m.imageid, m.mjd_obs, o.ra_psf, o.dec_psf, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, o.flags, m.filename cmf_file, i.name
--       from tcs_transient_objects o
-- inner join tcs_cmf_metadata m
--         on (o.tcs_cmf_metadata_id = m.id)
--  left join tcs_image_groups i
--         on (o.image_group_id = i.id)
--      union
    select r.id, r.transient_object_id, m.imageid, m.mjd_obs, r.ra_psf, r.dec_psf, r.psf_inst_mag, r.ap_mag, r.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, r.flags, m.filename cmf_file, i.name
      from tcs_transient_reobservations r
inner join tcs_cmf_metadata m
        on (r.tcs_cmf_metadata_id = m.id)
 left join tcs_image_groups i
        on (r.image_group_id = i.id)
     where i.group_type is null;


-- Postage Stamp Server Images --
create or replace view psdb_web_v_postage_stamp_server_images_presentation as
select ps.id, o.id object_id, ps.image_group_id, ps.image_type, ps.image_filename, ps.pss_filename, m.imageid diff_id, m.mjd_obs object_mjd, ps.mjd_obs stamp_mjd, ps.pss_error_code, concat(if(replace(database(),'_django','') != database(), replace(database(),'_django',''), 'panstarrs1'), '/', truncate(m.mjd_obs, 0), '/', ps.image_filename) filename
  from tcs_transient_objects o, tcs_postage_stamp_images ps, tcs_cmf_metadata m
 where m.id = o.tcs_cmf_metadata_id
   and o.image_group_id = ps.image_group_id
 union
select ps.id, r.transient_object_id object_id, ps.image_group_id, ps.image_type, ps.image_filename, ps.pss_filename, m.imageid diff_id, m.mjd_obs object_mjd, ps.mjd_obs stamp_mjd, ps.pss_error_code, concat(if(replace(database(),'_django','') != database(), replace(database(),'_django',''), 'panstarrs1'), '/', truncate(m.mjd_obs, 0), '/', ps.image_filename) filename
  from tcs_transient_reobservations r, tcs_postage_stamp_images ps, tcs_cmf_metadata m
 where m.id = r.tcs_cmf_metadata_id
   and r.image_group_id = ps.image_group_id
order by image_filename desc;


-- Postage Stamp Server Images - Better Version that doesn't               --
-- need to join with tcs_transient_objects or tcs_transient_reobservations --
-- which is useful if we want to fill in gaps with images not covered by   --
-- CMF files (and also MUCH quicker than the above)                        --
-- Removed diff_id from this query                                         --

-- 2010-09-15 KWS - Added new filter column to the view
-- 2014-03-10 KWS Don't pick out the finder images (reffinder or targetfinder
create or replace view psdb_web_v_postage_stamp_server_images_presentation_v2 as
select ps.id, 
--       substr(image_filename,1,instr(image_filename,'_')-1) object_id,
       ps.image_group_id,
       ps.image_type,
       ps.image_filename,
       ps.pss_filename,
--       substr(image_filename,instr(image_filename,'_')+1, instr(substr(image_filename,instr(image_filename,'_')+1),'_')-1) object_mjd,
       ps.mjd_obs stamp_mjd, ps.pss_error_code,
       concat(if(replace(database(),'_django','') != database(), replace(database(),'_django',''), 'panstarrs1'), '/', substr(image_filename,instr(image_filename,'_')+1, instr(image_filename,'.')-1-instr(image_filename,'_')), '/', ps.image_filename) filename,
       replace(ps.filter,'.00000','') filter
  from tcs_postage_stamp_images ps
 where ps.image_type != 'reffinder'
   and ps.image_type != 'targetfinder'
order by image_filename desc;

-- 2020-02-20 KWS New views that include zooniverse score.
-- 2020-09-30 KWS Added htm16ID so the views can be cone searched.
create or replace view psdb_web_v_followup_all_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where detection_list_id is not null
       and detection_list_id != 0
       and detection_list_id != 4
;


-- BAD objects
create or replace view psdb_web_v_followup_bad_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 0
;

-- CONFIRMED objects
create or replace view psdb_web_v_followup_conf_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 1
;

-- GOOD objects
create or replace view psdb_web_v_followup_good_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 2
;

-- POSSIBLE objects
create or replace view psdb_web_v_followup_poss_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 3
;

-- PENDING (EYEBALL) objects
create or replace view psdb_web_v_followup_pend_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 4
;

-- ATTIC objects
create or replace view psdb_web_v_followup_attic_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 5
;

-- ZOO objects
create or replace view psdb_web_v_followup_zoo_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 6
;

-- TBD objects
-- 2019-07-16 KWS Created two new views in particular for a Fast Track List.
create or replace view psdb_web_v_followup_tbd_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 7
;

-- FAST objects
create or replace view psdb_web_v_followup_fast_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.ra_psf,
           o.dec_psf,
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
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt,
           o.htm16ID
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
     where followup_id is not null
       and detection_list_id = 8
;


-- 2011-04-14 KWS User Defined Lists
create or replace view psdb_web_v_followup_userdefined as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.other_designation,
           o.local_comments,
           o.ra_psf,
           o.dec_psf,
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
           g.id object_id,
           o.classification_confidence,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target,
           z.score zooniverse_score,
           o.xt
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
inner join tcs_object_groups g
        on (o.id = g.transient_object_id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
 left join tcs_zooniverse_scores z
        on (o.id = z.transient_object_id)
;

