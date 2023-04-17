-- Table to store ATLAS forced photometry
-- 2017-08-07 KWS Added x,y,peakval,skyval,peakfit,dpeak,skyfit,flux,dflux,chin
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `atlas_forced_photometry`;

create table `atlas_forced_photometry` (
`id` bigint unsigned not null auto_increment,     -- autoincrementing detection id
`atlas_object_id` bigint(20) unsigned NOT NULL,   -- a reference to the unique object which tags this object
`expname` varchar(255),           -- = OBS
`mjd_obs` double,                 -- = MJD
`ra` double,                      -- = average RA at the time the photometry was done
`dec` double,                     -- = average Dec at the time the photometry was done
`filter` varchar(10),             -- = FILT
`mag` float,
`dm` float,
`snr` float,
`zp` float,
`x` float,
`y` float,
`peakval` float,
`skyval` float,
`peakfit` float,
`dpeak` float,
`skyfit` float,
`flux` float,
`dflux` float,
`chin` float,
`major` float,
`minor` float,
`snrdet` float,                   --  = Lower limit SNR above which we will mark as possible detection - e.g. 1
`snrlimit` float,                 --  = SNR above which we will mark as certain detections - e.g. 3
`apfit` float,
`date_inserted` datetime NOT NULL,   -- when was the detection inserted?
`limiting_mag` bool,                 -- is the mag a limiting mag?
`redo_photometry` bool,              -- option to overwrite this data point
PRIMARY KEY `key_id` (`id`),
KEY `idx_atlas_object_id` (`atlas_object_id`),
KEY `key_expname` (`expname`),
KEY `idx_mjd_obs` (`mjd_obs`),
UNIQUE KEY `idx_atlas_object_id_expname` (`atlas_object_id`,`expname`),
KEY `idx_date_inserted` (`date_inserted`)
) ENGINE=InnoDB;
