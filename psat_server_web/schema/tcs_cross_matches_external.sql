-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_cross_matches_external`;

create table `tcs_cross_matches_external` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
`transient_object_id` bigint(20) unsigned NOT NULL,
`external_designation` varchar(60) NOT NULL,
`type` varchar(40),
`host_galaxy` varchar(60),
`mag` float,
`discoverer` varchar(300),
`matched_list` varchar(100) NOT NULL,
`other_info` varchar(300),
`separation` float,
`comments` varchar(300),
`url` varchar(300),
`host_z` float,
`object_z` float,
`disc_date` datetime,
`disc_filter` varchar(50),
PRIMARY KEY `key_id` (`id`),
UNIQUE KEY `key_toi_ml_ed` (`transient_object_id`, `matched_list`, `external_designation`),
KEY `idx_transient_object_id` (`transient_object_id`),
KEY `idx_external_designation` (`external_designation`),
KEY `idx_url` (`url`)
) ENGINE=InnoDB
;
