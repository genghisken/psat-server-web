drop table if exists `tcs_cat_kepler_k2`;

-- EPIC_# or OTHER_NAME   | RA         |   DEC      | KpMag|caden|    COMMENT           | SourTyp | dK2E_as| radGA" |  gSDSS |  rSDSS |  iSDSS | redsft | zTyp|   number
-- -----------------------|------------|------------|------|-----|----------------------|---------|--------|--------|--------|--------|--------|--------|-----|---------
--               NGC_3640 | 170.278333 |   3.234722 | 10.7 |  30 |  EPIC_# = 0201675528 |xxx|  32 |   0.92 | 240.00 |  11.14 |  10.42 |  10.04 | 0.0042 |   1 |      1 |
-- 
-- 2014-11-14 KWS Renamed the table and added campaign column

create table `tcs_cat_kepler_k2` (
`id` int unsigned not null auto_increment,
`name` char(40) not null,
`ra_deg` double not null,
`dec_deg` double not null,
`kpmag` float,
`caden` tinyint unsigned,
`comment` varchar(30),
`sourtyp` tinyint unsigned,
`dk2e_as` float,
`radga` float,
`gsdss` float,
`rsdss` float,
`isdss` float,
`redsft` float,
`ztyp` tinyint unsigned,
`campaign` tinyint unsigned,
`htm20ID` bigint(20) unsigned not null,
`htm16ID` bigint(20) unsigned not null,
`cx` double not null,
`cy` double not null,
`cz` double not null,
PRIMARY KEY `idx_id` (`id`),
UNIQUE KEY `idx_name` (`name`),
KEY `idx_htm20ID` (`htm20ID`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_ra_deg_dec_deg` (`ra_deg`,`dec_deg`),
KEY `idx_campaign` (`campaign`)
) ENGINE=MyISAM;
