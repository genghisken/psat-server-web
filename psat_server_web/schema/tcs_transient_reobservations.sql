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
-- htm20ID - HTM level 20
-- htm16ID - HTM level 16
-- cx - Cartesian x-coordinate
-- cy - Cartesian y-coordinate
-- cz - Cartesian z-coordinate
-- id - A locally generated identifier - an internal database ID
-- transient_object_id - A reference to the parent object
-- tcs_cmf_metadata_id - A reference to CMF file metatdata table (mandatory)
--
-- date_inserted - The date that the data was originally ingested
-- date_modified - The date that the data was modified (e.g. due to any manual changes)
--
--

-- KWS - 19-06-2009 Added local_comments column to allow specific comments for recurrent objects.
-- KWS - 03-08-2009 Added tcs_images_id so that all images for all occurrences of an object can
--                  be referenced.
-- KWS - 10-12-2009 Added image_group_id (which will eventually replace tcs_images_id)
-- KWS - 08-06-2010 Added 7 new columns now included in CMF files for dipole calculations and
--                  also Locally calculated magnitude
--
-- KWS - 25-09-2010 Added 15 new columns now included in PS1_DV2 CMF
-- KWS - 02-03-2012 Added indexes to date_inserted and date_modified.
-- KWS - 22-03-2012 Added new column to deprecate object occurrence.
-- KWS - 12-11-2013 Added confidence_factor for individual detection occurrences. This gives us
--                  the option of combining them later if necessary.
-- 2016-04-29 KWS Added unique key to tcs_cmf_metadata_id, transient_object_id, ipp_idet to
--                prevent multiple accidental ingests of the same data.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `tcs_transient_reobservations`;

create table `tcs_transient_reobservations` (
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
`htm20ID` bigint(20) unsigned NOT NULL,
`htm16ID` bigint(20) unsigned NOT NULL,
`cx` double NOT NULL,
`cy` double NOT NULL,
`cz` double NOT NULL,
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
`tcs_cmf_metadata_id` bigint(20) unsigned NOT NULL,
`tcs_images_id` bigint(20) unsigned,
`transient_object_id` bigint(20) unsigned NOT NULL,
`date_inserted` datetime NOT NULL,
`date_modified` datetime,
`local_comments` varchar(255),
`postage_stamp_request_id` bigint unsigned,
`image_group_id` bigint unsigned,
`quality_threshold_pass` bool,
`locally_calculated_mag` float,
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
`deprecated` bool,
`confidence_factor` float,
PRIMARY KEY `key_id` (`id`),
KEY `key_transient_object_id` (`transient_object_id`),
KEY `idx_ipp_idet` (`ipp_idet`),
KEY `idx_htm20ID` (`htm20ID`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_ra_psf_dec_psf` (`ra_psf`,`dec_psf`),
KEY `idx_ps_req_id` (`postage_stamp_request_id`),
KEY `idx_image_group_id` (`image_group_id`),
KEY `idx_images_id` (`tcs_images_id`),
KEY `idx_q_threshold_pass` (`quality_threshold_pass`),
KEY `idx_date_inserted` (`date_inserted`),
KEY `idx_date_modified` (`date_modified`),
KEY `idx_metadata_id` (`tcs_cmf_metadata_id`),
KEY `idx_conf_factor` (`confidence_factor`),
UNIQUE KEY `idx_metadata_object_ippidet` (`tcs_cmf_metadata_id`, `transient_object_id`, `ipp_idet`)
) ENGINE=InnoDB;
