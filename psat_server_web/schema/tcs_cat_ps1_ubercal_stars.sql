-- Table to facilitate rapid crossmatching of photpipe detections.
-- Created to speed up crossmatching of fake sources injected into
-- ATLAS images.

drop table if exists `tcs_cat_ps1_ubercal_stars`;

create table `tcs_cat_ps1_ubercal_stars` (
`id` bigint unsigned not null,
`RA` double not null,
`Dec` double not null,
`g` float,
`dg` float,
`r` float,
`dr` float,
`i` float,
`di` float,
`z` float,
`dz` float,
`y` float,
`dy` float,
`htm16ID` bigint unsigned not null,
`htm20ID` bigint unsigned not null,
`cx` double not null,
`cy` double not null,
`cz` double not null,
PRIMARY KEY `key_id` (`id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_htm20ID` (`htm20ID`),
KEY `idx_RA_Dec` (`RA`,`Dec`)
) ENGINE=MyISAM;
