-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
-- ATLAS Heatmaps.
-- site = 01a, 02a, 03a, 04a, etc.
-- region = 0 to 4095 for a 128x128 region mask
drop table if exists `atlas_heatmaps`;

create table `atlas_heatmaps` (
`id` bigint unsigned not null auto_increment,
`site` varchar(10),
`region` int unsigned not null,
`ndet` int unsigned not null,
PRIMARY KEY `pk_id` (`id`),
UNIQUE KEY `idx_site_region` (`site`, `region`)
) ENGINE=InnoDB;
