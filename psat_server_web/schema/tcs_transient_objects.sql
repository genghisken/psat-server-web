--
-- NOTE:  All the ingest tables are exactly the same format.
--        A change of CMF file format will necessitate a change
--        of table structure, unless new columns are to be ignored.
--
-- This script was created as a result of examining old CMF files.
-- The format of the new CMF files is still to be confirmed.
--
-- The table consists of the original CMF columns plus the following:
--
-- local_designation - A locally generated object designation, based on object properties
-- local_comments - User inserted comments relating to the object
-- htm20ID - HTM level 20
-- htm16ID - HTM level 16
-- cx - Cartesian x-coordinate
-- cy - Cartesian y-coordinate
-- cz - Cartesian z-coordinate
-- id - A locally generated integer identifier based on RA/DEC
--      1 hhmmssss 1(N) or 0(S) ddmmsss 00
-- tcs_cmf_metadata_id - A reference to CMF file metatdata table (mandatory)
-- tcs_images_id - A reference to the images table (optional)
-- date_inserted - The date the object was ingested
-- date_modified - The date the object was updated (e.g. when reclassified)
-- object_classification - An unsigned integer representing object classification
--                         (see tcs_classification_flags)
-- followup_priority - An integer to help define the priority of future followup targets
-- external_reference_id - An identifier used to help keep track of followup targets
--                         across the PS1SC institutions
--
--
-- KWS0001 03-08-2009 Added follow_up_priority, external_reference_id.
-- KWS0001 27-11-2009 Added followup_id, postage_stamp_request_id.
-- KWS0001 10-12-2009 Added image_group_id (which will eventually replace tcs_images_id)
-- KWS0001 24-02-2010 Added followup_flag_date, detection_list, field, counter, ps1_designation
-- KWS0001 03-06-2010 Added zoo_request_id, locally_calculated_mag
-- KWS0001 08-06-2010 Added 7 new columns now included in CMF files for dipole calculations
--
-- KWS0001 25-09-2010 Added 15 new columns now included in PS1_DV2 CMF
-- KWS0001 14-01-2011 Added current_trend for lightcurve classification
-- KWS0001 03-05-2011 Changed the UNIQUE KEY for ps1_designation to NON UNIQUE.  This is because
--                    CfA choose these keys.  It is possible for QUB to therefore have more than
--                    one object with the same PS1 Designation
-- KWS0001 28-09-2011 Added an index to object_classification.
-- KWS0001 02-03-2012 Added indexes to date_inserted and date_modified.
-- KWS0001 22-03-2012 Added new column to deprecate object occurrence.
-- KWS0001 14-05-2013 Added new column to indicate TTI pair identification for 3pi Diffs

-- KWS0001 12-11-2013 Added processing_flags: 
--                    0000 0000 0000 0000 0000 0000 0000 0001 Bright Star Check
--                    0000 0000 0000 0000 0000 0000 0000 0010 Convolution Check
--                    0000 0000 0000 0000 0000 0000 0000 0100 Mover Check
--                    0000 0000 0000 0000 0000 0000 0000 1000 Ghost Check
--                    0000 0000 0000 0000 0000 0000 0001 0000 Location Map Generated
--
--                    Added classification_type.  What type of classification is this?
--                    0 = spectroscopic, 1 = suspected, 2 = photometric
-- 2015-02-23 KWS Added three new composite indexes in an attempt to improve web page
--                responsiveness.
-- 2016-04-29 KWS Added unique key to tcs_cmf_metadata_id, id, ipp_idet to prevent multiple
--                accidental ingests of the same data.
-- 2016-07-01 KWS Added sherlockClassification and zooniverse_score.
-- 2021-06-07 KWS Renamed classification_type (not used) to xt (crosstalk suspect) 1 = suspect.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `tcs_transient_objects`;

create table `tcs_transient_objects` (
`ipp_idet` int unsigned,
`x_psf` float,
`y_psf` float,
`x_psf_sig` float,
`y_psf_sig` float,
`ra_psf` double NOT NULL,
`dec_psf` double NOT NULL,
`posangle` float,
`pltscale` float,
`psf_inst_mag` float,
`psf_inst_mag_sig` float,
`ap_mag` float,
`ap_mag_radius` float,
`peak_flux_as_mag` float,
`cal_psf_mag` float,
`cal_psf_mag_sig` float,
`sky` float,
`sky_sigma` float,
`psf_chisq` float,
`cr_nsigma` float,
`ext_nsigma` float,
`psf_major` float,
`psf_minor` float,
`psf_theta` float,
`psf_qf` float,
`psf_ndof` int,
`psf_npix` int,
`moments_xx` float,
`moments_xy` float,
`moments_yy` float,
`flags` int unsigned,
`n_frames` smallint unsigned,
`padding` smallint,
`local_designation` varchar(40),
`local_comments` varchar(255),
`htm20ID` bigint(20) unsigned,
`htm16ID` bigint(20) unsigned,
`cx` double,
`cy` double,
`cz` double,
`id` bigint(20) unsigned NOT NULL,
`tcs_cmf_metadata_id` bigint(20) unsigned,
`tcs_images_id` bigint(20) unsigned,
`date_inserted` datetime NOT NULL,
`date_modified` datetime,
`object_classification` int unsigned,
`followup_priority` int unsigned,
`external_reference_id` varchar(40),
`followup_id` int unsigned,
`postage_stamp_request_id` bigint unsigned,
`image_group_id` bigint unsigned,
`detection_list_id` smallint unsigned,
`followup_flag_date` date,
`survey_field` varchar(10),
`followup_counter` int unsigned,
`ps1_designation` varchar(40),
`other_designation` varchar(40),
`confidence_factor` float,
`quality_threshold_pass` bool,
`locally_calculated_mag` float,
`zoo_request_id` bigint unsigned,
`psf_inst_flux` float,
`psf_inst_flux_sig` float,
`diff_npos` int,
`diff_fratio` float,
`diff_nratio_bad` float,
`diff_nratio_mask` float,
`diff_nratio_all` float,
`ap_flux` float,
`ap_flux_sig` float,
`ap_mag_raw` float,
`diff_r_m` float,
`diff_r_p` float,
`diff_sn_m` float,
`diff_sn_p` float,
`flags2` int unsigned,
`kron_flux` float,
`kron_flux_err` float,
`kron_flux_inner` float,
`kron_flux_outer` float,
`moments_r1` float,
`moments_rh` float,
`psf_qf_perfect` float,
`current_trend` varchar(40),
`observation_status` varchar(40),
`deprecated` bool,
`tti_pair` bool,
`processing_flags` int unsigned,
`updated_by` varchar(40),
`zooniverse_score` float,
`sherlockClassification` varchar(40),
`classification_confidence` float,
`xt` tinyint unsigned,
PRIMARY KEY `key_id` (`id`),
KEY `idx_ipp_idet` (`ipp_idet`),
KEY `idx_htm20ID` (`htm20ID`),
KEY `idx_htm16ID` (`htm16ID`),
UNIQUE KEY `idx_local_designation` (`local_designation`),
KEY `idx_ra_psf_dec_psf` (`ra_psf`,`dec_psf`),
KEY `idx_fu_priority` (`followup_priority`),
KEY `idx_fu_id` (`followup_id`),
KEY `idx_ps_req_id` (`postage_stamp_request_id`),
KEY `idx_ext_ref_id` (`external_reference_id`),
KEY `idx_image_group_id` (`image_group_id`),
KEY `idx_images_id` (`tcs_images_id`),
KEY `idx_fu_flag_date` (`followup_flag_date`),
KEY `idx_detection_list` (`detection_list_id`),
KEY `idx_survey_field` (`survey_field`),
KEY `idx_fu_counter` (`followup_counter`),
KEY `idx_ps1_designation` (`ps1_designation`),
KEY `idx_other_designation` (`other_designation`),
KEY `idx_conf_factor` (`confidence_factor`),
KEY `idx_q_threshold_pass` (`quality_threshold_pass`),
KEY `idx_metadata_id` (`tcs_cmf_metadata_id`),
KEY `idx_object_classification` (`object_classification`),
KEY `idx_date_inserted` (`date_inserted`),
KEY `idx_date_modified` (`date_modified`),
KEY `idx_observation_status` (`observation_status`),
KEY `idx_tti_pair` (`tti_pair`),
KEY `idx_processing_flags` (`processing_flags`),
KEY `idx_updated_by` (`updated_by`),
KEY `idx_sherlock_classification` (`sherlockClassification`),
KEY `idx_classification_confidence` (`classification_confidence`),
KEY `idx_xt` (`xt`),
KEY `idx_detection_list_id_object_classification` (detection_list_id, object_classification),
KEY `idx_detection_list_id_observation_status` (detection_list_id, observation_status),
KEY `idx_detection_list_id_confidence_factor` (detection_list_id, confidence_factor),
UNIQUE KEY `idx_metadata_object_ippidet` (`tcs_cmf_metadata_id`, `id`, `ipp_idet`)
) ENGINE=InnoDB;
