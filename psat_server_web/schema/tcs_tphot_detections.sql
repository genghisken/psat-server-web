-- Table to facilitate rapid crossmatching of tphot detections.
-- Created to speed up crossmatching of fake sources injected into
-- ATLAS images.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

-- The tphot header look like this (with ra, dec and mag added by Brian's code):
-- x        y     peakval  skyval  peakfit   dpeak  skyfit     flux     dflux    major  minor    phi  err chi/N ra dec mag

drop table if exists `tcs_tphot_detections`;

create table `tcs_tphot_detections` (
`id` bigint unsigned not null auto_increment,
`x` float,
`y` float,
`peakval` float,
`skyval` float,
`peakfit` float,
`dpeak` float,
`skyfit` float,
`flux` float,
`dflux` float,
`major` float,
`minor` float,
`phi` float,
`err` float,
`chi_N` float,
`ra` double not null,
`dec` double not null,
`mag` float,
`exptime` float,
`mjd` float,
`filter` char(3),
`zeropt` float,
`expname` varchar(256),
`htm16ID` bigint unsigned not null,
`htm20ID` bigint unsigned not null,
`cx` double not null,
`cy` double not null,
`cz` double not null,
PRIMARY KEY `key_id` (`id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_htm20ID` (`htm20ID`),
KEY `idx_ra_dec` (`ra`,`dec`),
KEY `idx_expname` (`expname`)
) ENGINE=InnoDB;
