-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
-- ###MJD          m      dm   uJy   duJy F err chi/N     RA       Dec        x        y     maj  min   phi  apfit  Sky    ZP    Stack
-- 58414.640780  21.185  1.429    12   17 o  0   1.05 161.19738  53.66524   356.28  1198.43 6.32 6.32   0.0 -0.200 18.42 19.32 161+53o58414
-- 58416.626060  20.278  0.406    28   11 o  0   1.10 161.19738  53.66524   356.28  1198.43 4.49 4.49   0.0 -0.200 18.57 18.88 161+53o58416


-- Table to store ATLAS forced photometry
-- 2017-08-07 KWS Added x,y,peakval,skyval,peakfit,dpeak,skyfit,flux,dflux,chin

drop table if exists `atlas_stacked_forced_photometry`;

create table `atlas_stacked_forced_photometry` (
`id` bigint unsigned not null auto_increment,     -- autoincrementing detection id
`atlas_object_id` bigint(20) unsigned NOT NULL,   -- a reference to the unique object which tags this object
`mjd` double,                 -- = MJD
`m` float,
`dm` float,
`ujy` float,
`dujy` float,
`f` varchar(10),             -- = FILT
`err` float,
`chin` float,
`ra` double,                      -- = average RA at the time the photometry was done
`dec` double,                     -- = average Dec at the time the photometry was done
`x` float,
`y` float,
`maj` float,
`min` float,
`phi` float,
`apfit` float,
`sky` float,
`zp` float,
`stack` varchar(20),
`date_inserted` datetime NOT NULL,   -- when was the detection inserted?
`redo_photometry` bool,              -- option to overwrite this data point
PRIMARY KEY `key_id` (`id`),
KEY `idx_atlas_object_id` (`atlas_object_id`),
KEY `idx_mjd` (`mjd`),
KEY `idx_date_inserted` (`date_inserted`)
) ENGINE=InnoDB;
