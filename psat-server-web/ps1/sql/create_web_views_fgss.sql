
-- create or replace view psdb_web_v_followup_pend_presentation as
--     select o.followup_id rank,
--            o.id,
--            substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
--            o.local_designation,
--            o.ps1_designation,
--            o.ra_psf,
--            o.dec_psf,
--            o.object_classification,
--            o.followup_flag_date,
--            o.observation_status,
--            o.current_trend,
--            s.earliest_mjd,
--            s.earliest_mag,
--            s.earliest_filter,
--            s.latest_mjd,
--            s.latest_mag,
--            s.latest_filter,
--            ct.description catalogue,
--            CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
--            min(c.separation) separation
--       from psdb_web_v_uniq_followup_transients_pend o
-- inner join tcs_cmf_metadata m
--         on (o.tcs_cmf_metadata_id = m.id)
--  left join tcs_cross_matches c
--         on (o.id = c.transient_object_id and c.association_type = 1)
--  left join tcs_catalogue_tables ct
--         on (c.catalogue_table_id = ct.id)
--  left join psdb_web_v_cat_sdss_stars_galaxies cat
--         on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
--  left join tcs_latest_object_stats s
--         on (o.id = s.id)
--   group by o.id;



-- NEW Followup Views for the Web Pages
-- Unfortunately we need one view per detection list (confirmed, good, bad, pending, attic, zoo).

-- The speed of this code might be improved by moving the catalogue calculations into the
-- tcs_latest_object_stats table (when it is calculated daily).

-- ALL objects (not BAD, not PEND)
-- 2011-05-27 KWS Selecting from another view is EXTREMELY INEFFICIENT and the lag has become
--                too noticeable.  Thus changing these views to select from tcs_transient_objects
--                and attaching the relevant WHERE clause to the end of the queries.
create or replace view psdb_web_v_followup_all_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id != 0
       and detection_list_id != 4
  group by o.id;



-- BAD objects
create or replace view psdb_web_v_followup_bad_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = 0
  group by o.id;


-- CONFIRMED objects
create or replace view psdb_web_v_followup_conf_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = 1
  group by o.id;


-- GOOD objects
create or replace view psdb_web_v_followup_good_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = 2
  group by o.id;


-- POSSIBLE objects
create or replace view psdb_web_v_followup_poss_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = 3
  group by o.id;


-- PENDING (EYEBALL) objects
create or replace view psdb_web_v_followup_pend_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = 4
  group by o.id;


-- ATTIC objects
create or replace view psdb_web_v_followup_attic_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = 5
  group by o.id;


-- ZOO objects
create or replace view psdb_web_v_followup_zoo_presentation as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id and c.association_type = 1)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
     where followup_id is not null
       and detection_list_id = 6
  group by o.id;


-- 2011-04-14 KWS User Defined Lists
create or replace view psdb_web_v_followup_userdefined as
    select o.followup_id rank,
           o.id,
           substr(m.filename, 1, instr(m.filename,'.')-1) survey_field,
           o.local_designation,
           o.ps1_designation,
           o.ra_psf,
           o.dec_psf,
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
           ct.description catalogue,
           CASE cat.type WHEN 6 THEN 'star' WHEN 3 THEN 'galaxy' ELSE NULL END catalogue_object_id,
           min(c.separation) separation,
           g.object_group_id,
           g.id object_id
      from tcs_transient_objects o
inner join tcs_cmf_metadata m
        on (o.tcs_cmf_metadata_id = m.id)
inner join tcs_object_groups g
        on (o.id = g.transient_object_id)
 left join tcs_cross_matches c
        on (o.id = c.transient_object_id)
 left join tcs_catalogue_tables ct
        on (c.catalogue_table_id = ct.id)
 left join psdb_web_v_cat_sdss_stars_galaxies cat
        on (cast(c.catalogue_object_id as unsigned) = cat.Objid)
 left join tcs_latest_object_stats s
        on (o.id = s.id)
  group by o.id, g.object_group_id;

