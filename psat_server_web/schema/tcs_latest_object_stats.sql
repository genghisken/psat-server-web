--
--  Latest Object Statistics.  Allows simplified queries to be made by the web interface
--  when presenting the followup lists.  HOWEVER, this table MUST be refreshed EVERY DAY.
--
--

-- 2014-02-20 KWS Added 2 new columns: external_crossmatches, discovery_target.
--                Also added indexes to the various columns.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `tcs_latest_object_stats`;

CREATE TABLE `tcs_latest_object_stats` (
  `id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `latest_mjd` double DEFAULT NULL,
  `latest_mag` float DEFAULT NULL,
  `latest_filter` varchar(80) DEFAULT NULL,
  `earliest_mjd` double DEFAULT NULL,
  `earliest_mag` float DEFAULT NULL,
  `earliest_filter` varchar(80) DEFAULT NULL,
  `ra_avg` double DEFAULT NULL,
  `dec_avg` double DEFAULT NULL,
  `catalogue` varchar(60) DEFAULT NULL,
  `catalogue_object_id` varchar(30) DEFAULT NULL,
  `separation` float DEFAULT NULL,
  `external_crossmatches` varchar(330) DEFAULT NULL,
  `discovery_target` varchar(80) DEFAULT NULL,
  `rms` float DEFAULT NULL,
  `latest_mjd_forced` double DEFAULT NULL,
  `latest_flux_forced` float DEFAULT NULL,
  `latest_dflux_forced` float DEFAULT NULL,
  `latest_filter_forced` varchar(10) DEFAULT NULL,
  `earliest_mjd_forced` double DEFAULT NULL,
  `earliest_flux_forced` float DEFAULT NULL,
  `earliest_dflux_forced` float DEFAULT NULL,
  `earliest_filter_forced` varchar(10) DEFAULT NULL,
  `earliest_pscamera` varchar(10) DEFAULT NULL,
  `latest_pscamera` varchar(10) DEFAULT NULL,
  `earliest_pscamera_forced` varchar(10) DEFAULT NULL,
  `latest_pscamera_forced` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_latest_mjd` (latest_mjd),
  KEY `idx_latest_mag` (latest_mag),
  KEY `idx_latest_filter` (latest_filter),
  KEY `idx_earliest_mjd` (earliest_mjd),
  KEY `idx_earliest_mag` (earliest_mag),
  KEY `idx_earliest_filter` (earliest_filter),
  KEY `idx_latest_mjd_forced` (latest_mjd_forced),
  KEY `idx_latest_flux_forced` (latest_flux_forced),
  KEY `idx_latest_dflux_forced` (latest_dflux_forced),
  KEY `idx_latest_filter_forced` (latest_filter_forced),
  KEY `idx_earliest_mjd_forced` (earliest_mjd_forced),
  KEY `idx_earliest_flux_forced` (earliest_flux_forced),
  KEY `idx_earliest_dflux_forced` (earliest_dflux_forced),
  KEY `idx_earliest_filter_forced` (earliest_filter_forced),
  KEY `idx_ra_avg` (ra_avg),
  KEY `idx_dec_avg` (dec_avg),
  KEY `idx_external_crossmatches` (external_crossmatches),
  KEY `idx_discovery_target` (discovery_target),
  KEY `idx_rms` (rms)
) ENGINE=InnoDB;
