-- Create Web Application Views. Should ONLY be executed on the Web Application DB

-- Direct views of PS1 database.
create or replace view tcs_transient_objects as select * from DATABASE.tcs_transient_objects;
create or replace view tcs_transient_reobservations as select * from DATABASE.tcs_transient_reobservations;
create or replace view tcs_cmf_metadata as select * from DATABASE.tcs_cmf_metadata;
create or replace view tcs_cross_matches as select * from DATABASE.tcs_cross_matches;
create or replace view tcs_images as select * from DATABASE.tcs_images;
create or replace view tcs_catalogue_tables as select * from DATABASE.tcs_catalogue_tables;
create or replace view tcs_classification_flags as select * from DATABASE.tcs_classification_flags;

-- 2010-01-12 KWS: New tables created for the Postage Stamp Server interaction
create or replace view tcs_image_groups as select * from DATABASE.tcs_image_groups;
create or replace view tcs_postage_stamp_images as select * from DATABASE.tcs_postage_stamp_images;
create or replace view tcs_postage_stamp_requests as select * from DATABASE.tcs_postage_stamp_requests;
create or replace view tcs_postage_stamp_status_codes as select * from DATABASE.tcs_postage_stamp_status_codes;
create or replace view tcs_detection_lists as select * from DATABASE.tcs_detection_lists;

-- 2010-01-12 KWS: New tables created for the Supernova Zoo interaction
create or replace view tcs_zoo_requests as select * from DATABASE.tcs_zoo_requests;

-- 2011-01-20 KWS: New statistics table
create or replace view tcs_latest_object_stats as select * from DATABASE.tcs_latest_object_stats;

-- 2011-04-01 KWS: User defined object groups tables
create or replace view tcs_object_group_definitions as select * from DATABASE.tcs_object_group_definitions;
create or replace view tcs_object_groups as select * from DATABASE.tcs_object_groups;

-- 2011-10-11 KWS: New tables for CfA Crossmatching.
create or replace view tcs_cfa_detections as select * from DATABASE.tcs_cfa_detections;
create or replace view tcs_cfa_to_ipp_lookup as select * from DATABASE.tcs_cfa_to_ipp_lookup;
create or replace view tcs_ipp_to_cfa_lookup as select * from DATABASE.tcs_ipp_to_cfa_lookup;

-- 2012-03-22 KWS: New table to show the general status of the transient server.
create or replace view tcs_processing_status as select * from DATABASE.tcs_processing_status;

-- 2013-02-12 KWS: New tables for telescope followup photometry
create or replace view tcs_followup_photometry as select * from DATABASE.tcs_followup_photometry;
create or replace view tcs_followup_telescopes as select * from DATABASE.tcs_followup_telescopes;
create or replace view tcs_followup_telescope_instruments as select * from DATABASE.tcs_followup_telescope_instruments;

-- 2013-03-01 KWS: New table for forced photometry
create or replace view tcs_forced_photometry as select * from DATABASE.tcs_forced_photometry;

-- 2013-10-21 KWS: New table for external crossmatches
create or replace view tcs_cross_matches_external as select * from DATABASE.tcs_cross_matches_external;

-- 2016-07-01 KWS: New table for object comments
create or replace view tcs_object_comments as select * from DATABASE.tcs_object_comments;

-- 2017-03-21 KWS: New Sherlock tables
create or replace view sherlock_crossmatches as select * from DATABASE.sherlock_crossmatches;
create or replace view sherlock_classifications as select * from DATABASE.sherlock_classifications;

-- 2017-03-21 KWS: New GW tables
create or replace view tcs_gravity_events as select * from DATABASE.tcs_gravity_events;
create or replace view tcs_gravity_event_annotations as select * from DATABASE.tcs_gravity_event_annotations;

-- 2020-05-11 KWS: New tcs_zooniverse_scores table for Zooniverse.
create or replace view tcs_zooniverse_scores as select * from DATABASE.tcs_zooniverse_scores;


-- The efficiency of the presentation web page query is vastly improved by joining against a view
-- of each type of object.  The downside of this that we have to use 7 views rather than one generic
-- view.  This is a pity, but the improvement from 20 sec to 0.4 sec for a query speaks for itself.

-- Generic view for all objects whose followup priority is not null and not in the bad list
create or replace view psdb_web_v_uniq_followup_transients as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id != 0
    and detection_list_id != 4;

-- Generic view for all "confirmed" objects whose followup priority is not null
create or replace view psdb_web_v_uniq_followup_transients_conf as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id = 1;

-- Generic view for all "good" objects whose followup priority is not null
create or replace view psdb_web_v_uniq_followup_transients_good as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id = 2;

-- Generic view for all "possible" objects whose followup priority is not null
create or replace view psdb_web_v_uniq_followup_transients_poss as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id = 3;

-- Generic view for all "bad" objects whose followup priority is not null
create or replace view psdb_web_v_uniq_followup_transients_bad as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id = 0;

-- Generic view for all "pending" objects whose followup priority is not null
create or replace view psdb_web_v_uniq_followup_transients_pend as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id = 4;

-- Generic view for all "attic" objects whose followup priority is not null
create or replace view psdb_web_v_uniq_followup_transients_attic as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id = 5;

-- Generic view for all "zoo" objects whose followup priority is not null
-- NOTE: These are the objects sent to the supernova zoo. We need to tag
--       which ones were sent when to stop multiple instances of the same
--       object being sent to the zoo.
create or replace view psdb_web_v_uniq_followup_transients_zoo as
 select *
   from tcs_transient_objects
  where followup_id is not null
    and detection_list_id = 6;




-- NEW: Get rid of superfluous columns & add new columns
create or replace view psdb_web_v_uniq_followup_transients_presentation_new as
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;







-- GENERIC VIEW of Followup Objects
create or replace view psdb_web_v_uniq_followup_transients_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- GENERIC VIEW of Confirmed Detections
create or replace view psdb_web_v_uniq_followup_transients_conf_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients_conf o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- GENERIC VIEW of Good Detections
create or replace view psdb_web_v_uniq_followup_transients_good_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients_good o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- GENERIC VIEW of Possible Detections
create or replace view psdb_web_v_uniq_followup_transients_poss_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients_poss o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- GENERIC VIEW of Bad Detections
create or replace view psdb_web_v_uniq_followup_transients_bad_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients_bad o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- GENERIC VIEW of Pending Detections
create or replace view psdb_web_v_uniq_followup_transients_pend_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients_pend o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- GENERIC VIEW of Attic Detections
create or replace view psdb_web_v_uniq_followup_transients_attic_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients_attic o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- GENERIC VIEW of Zoo Detections
create or replace view psdb_web_v_uniq_followup_transients_zoo_presentation as
--    select o.followup_id rank, o.id, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.filename, m.filename cmf_file
    select o.followup_id rank, o.id, o.local_designation, o.ps1_designation, o.ra_psf, o.dec_psf, m.mjd_obs, f.flag_name, replace(m.fpa_filter,'.00000','') filter, o.cal_psf_mag, o.followup_flag_date, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, substr(m.filename, 1, instr(m.filename,'.')-1) survey_field
      from psdb_web_v_uniq_followup_transients_zoo o
inner join tcs_classification_flags f
        on (o.object_classification = f.flag_id)
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
  group by o.id;

-- Recurrent Objects --
-- 2014-03-10 KWS Added group_type clause so that we don't pick out the finders
-- Note that Django models require a unique key.  Thus for the first part of the union, the ID field is selected twice, the second being renamed.
create or replace view psdb_web_v_recurrent_objects_presentation as
--    select o.id, o.id transient_object_id, m.imageid, m.mjd_obs, o.ra_psf, o.dec_psf, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, o.flags, m.filename cmf_file, i.name
--      from tcs_transient_objects o
-- inner join tcs_cmf_metadata m
--        on (o.tcs_cmf_metadata_id = m.id)
-- left join tcs_image_groups i
--        on (o.image_group_id = i.id)
--     union
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


-- 2010-01-28 KWS Re-vamped Presentation Views that don't need to refer an initial view of the objects table.
--                Here, we create a single view for each type of object we want to show - i.e. each bit of
--                the object_classfication bitmask.
--
-- NOTE: This approach needs to be re-evaluated. When Django-Pagination is used, it does a query
--       using limit = N and offset = N.  Doing this with true database tables yields almost instant
--       results.  Doing this with a view causes ALL rows to be requested and only the relevant N
--       rows to be displayed.  This greatly slows down the query (and for very large subset
--       of data this will generate an unacceptable GUI delay in rendering the result).

-- Type 1 (Unassociated Orphans) --
     create or replace view psdb_web_v_uniq_1_presentation as
     select o.id, o.ra_psf, o.dec_psf, m.mjd_obs, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join tcs_images i
        on (o.tcs_images_id = i.id)
     where object_classification & 1 = 1
  group by o.id;

-- Type 2 (Variable Stars) --
     create or replace view psdb_web_v_uniq_2_presentation as
     select o.id, o.ra_psf, o.dec_psf, m.mjd_obs, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join tcs_images i
        on (o.tcs_images_id = i.id)
     where object_classification & 2 = 2
  group by o.id;

-- Type 4 (Nuclear Transient) --
     create or replace view psdb_web_v_uniq_4_presentation as
     select o.id, o.ra_psf, o.dec_psf, m.mjd_obs, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join tcs_images i
        on (o.tcs_images_id = i.id)
     where object_classification & 4 = 4
  group by o.id;

-- Type 8 (Active Galactic Nucleus) --
     create or replace view psdb_web_v_uniq_8_presentation as
     select o.id, o.ra_psf, o.dec_psf, m.mjd_obs, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join tcs_images i
        on (o.tcs_images_id = i.id)
     where object_classification & 8 = 8
  group by o.id;

-- Type 16 (Supernova) --
     create or replace view psdb_web_v_uniq_16_presentation as
     select o.id, o.ra_psf, o.dec_psf, m.mjd_obs, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join tcs_images i
        on (o.tcs_images_id = i.id)
     where object_classification & 16 = 16
  group by o.id;

-- Type 32 (Associated Orphan) --
     create or replace view psdb_web_v_uniq_32_presentation as
     select o.id, o.ra_psf, o.dec_psf, m.mjd_obs, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join tcs_images i
        on (o.tcs_images_id = i.id)
     where object_classification & 32 = 32
  group by o.id;

-- Type 64 (Not used yet in the new classification scheme) --
     create or replace view psdb_web_v_uniq_64_presentation as
     select o.id, o.ra_psf, o.dec_psf, m.mjd_obs, o.psf_inst_mag, o.ap_mag, o.cal_psf_mag, replace(m.fpa_filter,'.00000','') filter, ct.description catalogue, c.catalogue_object_id, min(c.separation) separation, i.target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join tcs_images i
        on (o.tcs_images_id = i.id)
     where object_classification & 64 = 64
  group by o.id;



-- NEW Followup Views for the Web Pages
-- Unfortunately we need one view per detection list (confirmed, good, bad, pending, attic, zoo).

-- The speed of this code might be improved by moving the catalogue calculations into the
-- tcs_latest_object_stats table (when it is calculated daily).

-- ALL objects (not BAD, not PEND)
-- 2011-05-27 KWS Selecting from another view is EXTREMELY INEFFICIENT and the lag has become
--                too noticeable.  Thus changing these views to select from tcs_transient_objects
--                and attaching the relevant WHERE clause to the end of the queries.

-- 2013-10-23 KWS Added (machine learning) confidence_factor to all views below, including custom lists.
-- 2013-02-20 KWS Added added external_crossmatches and discovery_target to all views below.
create or replace view psdb_web_v_followup_all_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
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
       --  ct.description catalogue,
       --  c.catalogue_object_id,
       --  min(c.separation) separation
           s.catalogue,
           s.catalogue_object_id,
           s.separation,
           o.confidence_factor,
           s.external_crossmatches,
           s.discovery_target
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
-- left join tcs_cross_matches c
--        on (o.id = c.transient_object_id)
-- left join tcs_catalogue_tables ct
--        on (c.catalogue_table_id = ct.id)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where detection_list_id is not null
       and detection_list_id != 0
       and detection_list_id != 4
--       and followup_id is not null
-- group by o.id;
;


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

-- 2011-10-11 KWS CfA Crossmatching views
-- This needs to be created inside the django schema, which means that
-- the tcs_cfa_detections and tcs_ipp_to_cfa_lookup tables must be visible
-- in the schema.

-- Only show objects that are NOT in the CfA Attic

create or replace view psdb_web_v_ipp_to_cfa_crossmatch
as
select o.id, 
       o.local_designation,
       o.followup_id,
       o.detection_list_id,
       o.followup_flag_date,
       o.ra_psf,
       o.dec_psf,
       substr(m.filename,1,4) field,
       cfa.eventID,
       cfa.cfa_designation,
       cfa.alertstatus,
       cfa.date,
       cfa.raDeg,
       cfa.decDeg,
       cfa.PS1name,
       lu.separation
from tcs_ipp_to_cfa_lookup lu
inner join
  tcs_transient_objects o
on
  (o.id = lu.transient_object_id)
inner join
  tcs_cmf_metadata m
on
  (m.id = o.tcs_cmf_metadata_id)
left join
  tcs_cfa_detections cfa
on
  (cfa.eventID = lu.eventID)
where cfa.attic != 1 or cfa.attic is null;


-- Only show objects that are in the CfA Attic
create or replace view psdb_web_v_ipp_to_cfa_crossmatch_attic
as
select o.id, 
       o.local_designation,
       o.followup_id,
       o.detection_list_id,
       o.followup_flag_date,
       o.ra_psf,
       o.dec_psf,
       substr(m.filename,1,4) field,
       cfa.eventID,
       cfa.cfa_designation,
       cfa.alertstatus,
       cfa.date,
       cfa.raDeg,
       cfa.decDeg,
       cfa.PS1name,
       lu.separation
from tcs_ipp_to_cfa_lookup lu
inner join
  tcs_transient_objects o
on
  (o.id = lu.transient_object_id)
inner join
  tcs_cmf_metadata m
on
  (m.id = o.tcs_cmf_metadata_id)
left join
  tcs_cfa_detections cfa
on
  (cfa.eventID = lu.eventID)
where cfa.attic = 1;


-- Only show objects that are NOT in the CfA Attic
create or replace view psdb_web_v_cfa_to_ipp_crossmatch
as
select o.id, 
       o.local_designation,
       o.followup_id,
       o.detection_list_id,
       o.followup_flag_date,
       o.ra_psf,
       o.dec_psf,
       substr(m.filename,1,4) field,
       cfa.eventID,
       cfa.cfa_designation,
       cfa.alertstatus,
       cfa.date,
       cfa.raDeg,
       cfa.decDeg,
       cfa.PS1name,
       lu.separation
from tcs_cfa_to_ipp_lookup lu
inner join
  tcs_cfa_detections cfa
on
  (cfa.eventID = lu.eventID)
left join
  tcs_transient_objects o
on
  (o.id = lu.transient_object_id)
left join
  tcs_cmf_metadata m
on
  (m.id = o.tcs_cmf_metadata_id)
where cfa.attic != 1 or cfa.attic is null;


-- Only show objects that are in the CfA Attic
create or replace view psdb_web_v_cfa_to_ipp_crossmatch_attic
as
select o.id, 
       o.local_designation,
       o.followup_id,
       o.detection_list_id,
       o.followup_flag_date,
       o.ra_psf,
       o.dec_psf,
       substr(m.filename,1,4) field,
       cfa.eventID,
       cfa.cfa_designation,
       cfa.alertstatus,
       cfa.date,
       cfa.raDeg,
       cfa.decDeg,
       cfa.PS1name,
       lu.separation
from tcs_cfa_to_ipp_lookup lu
inner join
  tcs_cfa_detections cfa
on
  (cfa.eventID = lu.eventID)
left join
  tcs_transient_objects o
on
  (o.id = lu.transient_object_id)
left join
  tcs_cmf_metadata m
on
  (m.id = o.tcs_cmf_metadata_id)
where cfa.attic = 1;

