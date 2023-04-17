-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_followup_photometry`;

create table `tcs_followup_photometry` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
`transient_object_id` bigint(20) unsigned NOT NULL,
`telescope_instrument_id` smallint unsigned NOT NULL,
`mjd` double NOT NULL,
`filter` varchar(20),
`mag` float,
`magerr` float,
PRIMARY KEY `key_id` (`id`),
KEY `key_mjd` (`mjd`),
UNIQUE KEY `idx_transient_telescope_mjd_filter_mag` (`transient_object_id`, `telescope_instrument_id`, `mjd`, `filter`, `mag`),
KEY `key_transient_object_id` (`transient_object_id`)
) ENGINE=InnoDB;

