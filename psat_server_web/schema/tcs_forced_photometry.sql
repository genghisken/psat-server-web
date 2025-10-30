-- Forced Photmetry Table
-- 2013-02-27 KWS Ditched the old forced photometry table definition in favour of
--                this one, which is 39 columns from CMF table + survey field, skycell,
--                filter, mjd_obs, exptime.
-- 2015-10-13 KWS Forgot to add zero_pt.
-- 2021-12-28 KWS Added pscamera to the list of columns.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
-- 2025-06-30 KWS Added new column "type" whose value is 0 for diff and 1 for reduced (new).
drop table if exists `tcs_forced_photometry`;

create table `tcs_forced_photometry` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
`postage_stamp_request_id` bigint unsigned,
`transient_object_id` bigint(20) unsigned NOT NULL,
`rownum` int,
`skycell` varchar(10),
`mjd_obs` double,
`exptime` float,
`zero_pt` float,
`filter` varchar(20),
`fpa_id` varchar(20),
`x_psf` float,
`y_psf` float,
`x_psf_sig` float,
`y_psf_sig` float,
`posangle` float,
`pltscale` float,
`psf_inst_mag` float,
`psf_inst_mag_sig` float,
`psf_inst_flux` float,
`psf_inst_flux_sig` float,
`ap_mag` float,
`ap_mag_radius` float,
`peak_flux_as_mag` float,
`cal_psf_mag` float,
`cal_psf_mag_sig` float,
`ra_psf` double NOT NULL,
`dec_psf` double NOT NULL,
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
`diff_npos` int,
`diff_fratio` float,
`diff_nratio_bad` float,
`diff_nratio_mask` float,
`diff_nratio_all` float,
`flags` int unsigned,
`n_frames` smallint unsigned,
`padding` smallint,
`zero_pt_skycell_corrected` float,
`pscamera` varchar(10),
`fptype` tinyint not null default 0,
PRIMARY KEY `key_id` (`id`),
UNIQUE KEY `idx_transient_object_id_fpa_id_fptype` (`transient_object_id`,`fpa_id`,`fptype`),
KEY `idx_ra_psf_dec_psf` (`ra_psf`,`dec_psf`),
KEY `idx_ps_req_id` (`postage_stamp_request_id`),
KEY `idx_skycell` (`skycell`),
KEY `key_mjd_obs` (`mjd_obs`),
KEY `key_exptime` (`exptime`),
KEY `key_transient_object_id` (`transient_object_id`)
) ENGINE=InnoDB;

