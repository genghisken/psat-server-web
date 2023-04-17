drop table if exists `atlas_metadataddc`;
--
-- atlas_metadataddc.sql
-- Author: K. W. Smith
-- Initially created by generateATLASSchemaAndCPPClasses.py
-- on 2017-06-06
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
CREATE TABLE `atlas_metadataddc` (
`id` bigint unsigned not null auto_increment,     -- autoincrementing detection id
`filename` varchar(255),
`obs` varchar(60), 
`obj` varchar(60), 
`filt` varchar(10), 
`mjd` double, 
`texp` float, 
`ra` double, 
`dec` double, 
`pa` float, 
`nx` smallint unsigned, 
`ny` smallint unsigned, 
`rad` int, 
`fwmaj` float, 
`fwmin` float, 
`psfpa` float, 
`scale` float, 
`long` float, 
`lat` float, 
`elev` float, 
`rarms` float, 
`decrms` float, 
`magzpt` float, 
`skymag` float, 
`cloud` float, 
`mag5sig` float, 
`az` float, 
`alt` float, 
`lambda` float, 
`beta` float, 
`sunelong` float, 
`apfit` float,
`bckgnd` int,
`gain` float,
`psfphi` float,
`ddcver` varchar(10),
`input` varchar(255),
`reference` varchar(255),
`htm16ID` bigint unsigned,
`date_inserted` datetime NOT NULL,   -- when was the detection inserted?
PRIMARY KEY `key_id` (`id`),
UNIQUE KEY `key_filename_mjd` (`filename`,`mjd`),
KEY `idx_mjd` (`mjd`),
UNIQUE KEY `key_obs` (`obs`),
KEY `idx_texp` (`texp`),
KEY `idx_filename` (`filename`),
KEY `idx_input` (`input`),
KEY `idx_reference` (`reference`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_date_inserted` (`date_inserted`),
KEY `idx_ra_dec` (`ra`,`dec`)
) ENGINE=InnoDB;
