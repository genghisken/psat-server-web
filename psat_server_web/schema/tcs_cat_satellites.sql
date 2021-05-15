drop table if exists `tcs_cat_satellites`;

create table `tcs_cat_satellites` (
`id` int unsigned not null auto_increment,
`name` char(40) not null,
`mjd` double not null,
`ra_deg` double not null,
`dec_deg` double not null,
`apparent_mag` float,
`htm10ID` int unsigned not null,
`htm13ID` int unsigned not null,
`htm16ID` bigint(20) unsigned not null,
PRIMARY KEY `idx_id` (`id`),
KEY `idx_name` (`name`),
KEY `idx_htm10ID` (`htm10ID`),
KEY `idx_htm13ID` (`htm13ID`),
KEY `idx_htm16ID` (`htm16ID`),
UNIQUE KEY `idx_ra_deg_dec_deg` (`ra_deg`,`dec_deg`)
) ENGINE=MyISAM;
