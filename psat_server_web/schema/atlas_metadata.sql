-- 2015-10-21 KWS Added HTM level 16 index for boresight RA and Dec.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

-- Header example as of 2015-11-02

-- OBS=      02a57320o0568o  knownast
-- OBJ=      TA038N62           0
-- MJD=      57320.579942           0
-- FILT=     o           0
-- PA=       -0.289           0
-- TEXP=     30.000           0
-- NX=       10560           0
-- NY=       10560           0
-- RAD=      7467           0
-- SCALE=    1.862           0
-- LONG=     -156.2570           0
-- LAT=      20.7075           0
-- ELEV=     3062.6580           0
-- RA=       36.53434           0
-- DEC=      61.89507           0
-- RARMS=    0.140           0
-- DECRMS=   0.140           0
-- MAGZPT=   21.310           0
-- SKYMAG=   19.39           0
-- CLOUD=    1.000           0
-- MAG5SIG=  18.42           0
-- AZ=       333.41627           0
-- ALT=      36.68003           0
-- LAMBDA=   58.102           0
-- BETA=     44.246           0
-- SUNELONG= 129.966           0


drop table if exists `atlas_metadata`;

CREATE TABLE `atlas_metadata` (
  `id` bigint(20) unsigned not null auto_increment,
  `filename` varchar(255),
  `expname` varchar(255),           -- = OBS
  `object` varchar(255),            -- = OBJ
  `mjd_obs` double,                 -- = MJD
  `filter` varchar(10),             -- = FILT
  `pa` float,                       -- = PA
  `exptime` float,                  -- = TEXP
  `nx` smallint unsigned,           -- = NX
  `ny` smallint unsigned,           -- = NY
  `rad` int,                        -- = RAD
  `scale` float,                    -- = SCALE
  `longitude` float,                -- = LONG
  `latitude` float,                 -- = LAT
  `elev` float,                     -- = ELEV
  `ra` double,                      -- = RA (boresight RA)
  `dec` double,                     -- = DEC (boresight Dec)
  `rarms` float,                    -- = RARMS
  `decrms` float,                   -- = DECRMS
  `zp` float,                       -- = MAGZPT
  `skymag` float,                   -- = SKYMAG
  `cloud` float,                    -- = CLOUD
  `mag5sig` float,                  -- = MAG5SIG
  `az` float,                       -- = AZ
  `alt` float,                      -- = ALT
  `lambda` float,                   -- = LAMBDA
  `beta` float,                     -- = BETA
  `sunelong` float,                 -- = SUNELONG
  `htm16ID` bigint(20) unsigned, -- HTM level 16 value for boresight ra and dec
  `input` varchar(255),
  `reference` varchar(255),
  `date_inserted` datetime NOT NULL,   -- when was the file inserted
  PRIMARY KEY `key_id` (`id`),
  UNIQUE KEY `key_filename_mjd_obs` (`filename`,`mjd_obs`),
  KEY `idx_mjd_obs` (`mjd_obs`),
  UNIQUE KEY `key_expname` (`expname`),
  KEY `idx_exptime` (`exptime`),
  KEY `idx_filename` (`filename`),
  KEY `idx_input` (`input`),
  KEY `idx_reference` (`reference`),
  KEY `idx_date_inserted` (`date_inserted`),
  KEY `idx_htm16ID` (`htm16ID`)
) ENGINE=InnoDB;
