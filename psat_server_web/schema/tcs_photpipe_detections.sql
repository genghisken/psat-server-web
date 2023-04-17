-- Table to facilitate rapid crossmatching of photpipe detections.
-- Created to speed up crossmatching of fake sources injected into
-- ATLAS images.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `tcs_photpipe_detections`;

create table `tcs_photpipe_detections` (
`id` bigint unsigned not null auto_increment,
`RA` double not null,
`Dec` double not null,
`Xpos` float,
`Ypos` float,
`angle` float,
`M` float,
`dM` float,
`peakflux` float,
`sky` float,
`chisqr` float,
`extendedness` float,
`FWHM1` float,
`FWHM2` float,
`pixchk_Nneg` int,
`pixchk_Nmask` int,
`sigx` float,
`sigxy` float,
`sigy` float,
`flag` int unsigned,
`Nmask` smallint unsigned,
`type` smallint,
`flux` float,
`dflux` float,
`pixchk_Npos` int,
`pixchk_Fpos` float,
`pixchk_Fneg` float,
`pixchk_Ntot` float,
`class` float,
`FWHM` float,
`mask` int unsigned,
`exptime` float,
`mjd` float,
`zeropt` float,
`imagename` varchar(256),
`htm16ID` bigint unsigned not null,
`htm20ID` bigint unsigned not null,
`cx` double not null,
`cy` double not null,
`cz` double not null,
PRIMARY KEY `key_id` (`id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_htm20ID` (`htm20ID`),
KEY `idx_RA_Dec` (`RA`,`Dec`),
KEY `idx_imagename` (`imagename`)
) ENGINE=InnoDB;
