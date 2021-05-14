--
--  Latest Object Statistics.  Allows simplified queries to be made by the web interface
--  when presenting the followup lists.  HOWEVER, this table MUST be refreshed EVERY DAY.
--
--

-- 2014-02-20 KWS Added 2 new columns: external_crossmatches, discovery_target.
--                Also added indexes to the various columns.

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
  PRIMARY KEY (`id`),
  KEY `idx_latest_mjd` (latest_mjd),
  KEY `idx_latest_mag` (latest_mag),
  KEY `idx_latest_filter` (latest_filter),
  KEY `idx_earliest_mjd` (earliest_mjd),
  KEY `idx_earliest_mag` (earliest_mag),
  KEY `idx_earliest_filter` (earliest_filter),
  KEY `idx_ra_avg` (ra_avg),
  KEY `idx_dec_avg` (dec_avg),
  KEY `idx_external_crossmatches` (external_crossmatches),
  KEY `idx_discovery_target` (discovery_target),
  KEY `idx_rms` (rms)
) ENGINE=MyISAM;
