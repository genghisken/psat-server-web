-- Main schema creation script.

-- 2011-06-23 KWS added object groups tables and functions

source tcs_transient_objects.sql;
source tcs_transient_reobservations.sql;
source tcs_cmf_metadata.sql;
source tcs_cross_matches.sql;
source tcs_catalogue_tables.sql;
source tcs_classification_flags.sql;
source tcs_images.sql;
source tcs_classification_history.sql;
source tcs_search_parameters.sql;
source tcs_parameter_definitions.sql;
source tcs_image_groups.sql;
source tcs_postage_stamp_images.sql;
source tcs_postage_stamp_requests.sql;
source tcs_postage_stamp_status_codes.sql;
source tcs_detection_lists.sql;
source tcs_forced_photometry.sql;
source tcs_zoo_requests.sql;
source tcs_latest_object_stats.sql;
source tcs_object_groups.sql;
source tcs_object_group_definitions.sql;

-- Views
-- 2013-05-28 KWS These views are no longer required
-- source create_views.sql;
-- source create_catalogue_views.sql;

-- New functions to allow lunation selection
source tcs_function_lunation.sql;
source tcs_function_mjdlunation.sql;

-- New CfA crossmatching tables
source tcs_cfa_detections.sql;
source tcs_ipp_to_cfa_lookup.sql;
source tcs_cfa_to_ipp_lookup.sql;

-- New Processing Status table
source tcs_processing_status.sql;

-- Photometry from other telescopes
source tcs_followup_photometry.sql;
source tcs_followup_telescope_instruments.sql;
source tcs_followup_telescopes.sql;

-- 2013-11-14 KWS External Crossmatching table
source tcs_cross_matches_external.sql;

-- 2016-01-15 KWS New ATLAS tables
-- 2016-04-26 KWS Added atlas_diff_moments and tcs_object_comments
source atlas_diff_objects.sql;
source atlas_diff_detections.sql;
source atlas_diff_moments.sql;
source atlas_metadata.sql;
source tcs_object_comments.sql;

-- 2017-06-06 KWS New ATLAS tables for DDC files
source atlas_metadataddc.sql
source atlas_detectionsddc.sql

-- 2016-07-01 KWS Added tcs_tns_requests
source tcs_tns_requests.sql;

-- 2017-06-16 KWS Added tcs_gravity_events and tcs_gravity_event_annotations
source tcs_gravity_events.sql
source tcs_gravity_event_annotations.sql
source sherlock_crossmatches.sql
source sherlock_classifications.sql

-- 2017-11-02 KWS Added missing atlas_forced_photometry table
source atlas_forced_photometry.sql;

-- 2018-01-25 KWS New table for cacheing detections in exposure subcells.
source atlas_diff_subcells.sql;
source atlas_diff_subcell_logs.sql;

-- 2019-06-06 KWS New atlas_stacked_forced_photometry table.
source atlas_stacked_forced_photometry.sql;

-- 2020-05-11 KWS Added new tcs_zooniverse_scores table.
source tcs_zooniverse_scores.sql;

-- 2021-03-11 KWS Added atlas_diff_logs table.
source atlas_diff_logs.sql;

-- 2022-08-16 KWS Added atlas_heatmaps table.
source atlas_heatmaps.sql;

-- 2023-04-18 KWS Create mjdnow() function.
source mjdnow.sql;

-- 2023-06-02 KWS Added tcs_gravity_alerts table.
source tcs_gravity_alerts.sql;

-- 2024-01-17 KWS Added new tcs_vra_probabilities table.
source tcs_vra_probabilities.sql;
