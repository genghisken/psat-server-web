--
-- tcs_postage_stamp_images table.
--
-- 2010-06-03 KWS Added filter, mask_percentage and core_pixels_unmaksed columns
--                Note that the definition of "core" pixels may change, but this
--                is currently hard wired to the core whose width is 20% of the
--                image width (i.e. 60 pixels wide for a 300 pixel image).
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_postage_stamp_images`;

create table `tcs_postage_stamp_images` (
`id` bigint unsigned not null auto_increment,
`image_type` varchar(20) not null,
`image_filename` varchar(255) not null,
`pss_filename` varchar(255),
`mjd_obs` double,
`image_group_id` bigint unsigned not null,
`pss_error_code` smallint not null,
`filter` varchar(80),
`mask_ratio` float,
`mask_ratio_at_core` float,
PRIMARY KEY `pk_id` (`id`),
KEY `idx_image_type` (`image_type`),
KEY `idx_image_group_id` (`image_group_id`),
KEY `idx_image_filename` (`image_filename`)
) ENGINE=InnoDB;

