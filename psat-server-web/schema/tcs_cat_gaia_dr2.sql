CREATE TABLE `tcs_cat_gaia_dr2` (
`solution_id` bigint,
`designation` varchar(40),
`source_id` bigint unsigned,
`random_index` bigint,
`ref_epoch` double,
`ra` double NOT NULL,
`ra_error` double,
`dec` double NOT NULL,
`dec_error` double,
`parallax` double,
`parallax_error` double,
`parallax_over_error` float,
`pmra` double,
`pmra_error` double,
`pmdec` double,
`pmdec_error` double,
`ra_dec_corr` float,
`ra_parallax_corr` float,
`ra_pmra_corr` float,
`ra_pmdec_corr` float,
`dec_parallax_corr` float,
`dec_pmra_corr` float,
`dec_pmdec_corr` float,
`parallax_pmra_corr` float,
`parallax_pmdec_corr` float,
`pmra_pmdec_corr` float,
`astrometric_n_obs_al` int,
`astrometric_n_obs_ac` int,
`astrometric_n_good_obs_al` int,
`astrometric_n_bad_obs_al` int,
`astrometric_gof_al` float,
`astrometric_chi2_al` float,
`astrometric_excess_noise` double,
`astrometric_excess_noise_sig` double,
`astrometric_params_solved` tinyint unsigned,
`astrometric_primary_flag` bool,
`astrometric_weight_al` float,
`astrometric_pseudo_colour` double,
`astrometric_pseudo_colour_error` double,
`mean_varpi_factor_al` float,
`astrometric_matched_observations` smallint,
`visibility_periods_used` smallint,
`astrometric_sigma5d_max` float,
`frame_rotator_object_type` int,
`matched_observations` smallint,
`duplicated_source` bool,
`phot_g_n_obs` int,
`phot_g_mean_flux` double,
`phot_g_mean_flux_error` double,
`phot_g_mean_flux_over_error` float,
`phot_g_mean_mag` float,
`phot_bp_n_obs` int,
`phot_bp_mean_flux` double,
`phot_bp_mean_flux_error` double,
`phot_bp_mean_flux_over_error` float,
`phot_bp_mean_mag` float,
`phot_rp_n_obs` int,
`phot_rp_mean_flux` double,
`phot_rp_mean_flux_error` double,
`phot_rp_mean_flux_over_error` float,
`phot_rp_mean_mag` float,
`phot_bp_rp_excess_factor` float,
`phot_proc_mode` tinyint unsigned,
`bp_rp` float,
`bp_g` float,
`g_rp` float,
`radial_velocity` double,
`radial_velocity_error` double,
`rv_nb_transits` int,
`rv_template_teff` float,
`rv_template_logg` float,
`rv_template_fe_h` float,
`phot_variable_flag` varchar(40),
`l` double,
`b` double,
`ecl_lon` double,
`ecl_lat` double,
`priam_flags` bigint,
`teff_val` float,
`teff_percentile_lower` float,
`teff_percentile_upper` float,
`a_g_val` float,
`a_g_percentile_lower` float,
`a_g_percentile_upper` float,
`e_bp_min_rp_val` float,
`e_bp_min_rp_percentile_lower` float,
`e_bp_min_rp_percentile_upper` float,
`flame_flags` bigint,
`radius_val` float,
`radius_percentile_lower` float,
`radius_percentile_upper` float,
`lum_val` float,
`lum_percentile_lower` float,
`lum_percentile_upper` float,
`htm10ID` int NOT NULL,
`htm13ID` int NOT NULL,
`htm16ID` bigint unsigned NOT NULL,
PRIMARY KEY `pk_source_id` (source_id),
KEY `idx_ra` (`ra`),
KEY `idx_dec` (`dec`),
KEY `idx_ra_dec` (`ra`,`dec`),
KEY `idx_htm10ID` (`htm10ID`),
KEY `idx_htm13ID` (`htm13ID`),
KEY `idx_htm16ID` (`htm16ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci