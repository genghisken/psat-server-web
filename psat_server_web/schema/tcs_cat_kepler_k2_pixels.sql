drop table if exists `tcs_cat_kepler_k2_pixels`;

-- #kepid,ra,dec,module,output,row,column
create table `tcs_cat_kepler_k2_pixels` (
`id` int unsigned not null auto_increment,
`kepid` char(40) not null,
`ra_deg` double not null,
`dec_deg` double not null,
`module` int,
`output` int,
`row` int,
`column` int,
`campaign` tinyint unsigned,
`htm20ID` bigint(20) unsigned not null,
`htm16ID` bigint(20) unsigned not null,
`cx` double not null,
`cy` double not null,
`cz` double not null,
PRIMARY KEY `idx_id` (`id`),
KEY `idx_kepid` (`kepid`),
KEY `idx_htm20ID` (`htm20ID`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_ra_deg_dec_deg` (`ra_deg`,`dec_deg`),
KEY `idx_campaign` (`campaign`)
) ENGINE=MyISAM;
