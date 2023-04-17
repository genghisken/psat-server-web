-- This table is created temporarily inside MySQL, but this data will eventally be
-- stored in a "big data" database table.

-- The data is extracted by dophot, NOT tphot.  We could also do with the FITS header
-- from the files, or just use the .obs files.  Do we ultimately want to store the data
-- in a FLAT table structure?  In which case we should have columns below for expname,
-- exptime, mjd, etc.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

-- The dophot header look like this, with one example row added.  idx and Type are integers, the rest are floats. RA and Dec should be stored as doubles: 
--    RA        Dec       m       idx Type  xtsk     ytsk    fitmag dfitmag     sky       major    minor    phi    probgal     apmag dapmag     apsky  ap-fit
-- 193.69785  35.18475  12.136      3  2  4261.47    64.83  -13.255  0.000   1063.14     6.851     3.058    2.52  0.000E+00   99.999  0.000      0.00   0.000



drop table if exists `atlas_detections`;

create table `atlas_detections` (
`id` bigint unsigned not null auto_increment,     -- autoincrementing detection id
`atlas_object_id` bigint(20) unsigned NOT NULL,   -- a reference to the unique object which tags this object
`dphot_id` int unsigned not null,                 -- the internal id of the detection (unique per file)
`ra` double,
`dec` double,
`m` float,
`idx` int unsigned,
`type` tinyint unsigned,
`xtsk` float,
`ytsk` float,
`fitmag` float,
`dfitmag` float,
`sky` float,
`major` float,
`minor` float,
`phi` float,
`probgal` float,
`apmag` float,
`dapmag` float,
`apsky` float,
`ap_fit` float,
`htm16ID` bigint unsigned not null,
`jtindex` int unsigned,
`date_inserted` datetime NOT NULL,   -- when was the detection inserted?
`date_modified` datetime,            -- when was the detection modified?
`image_group_id` bigint unsigned, -- a reference to the group of images that refers to this detection
`quality_threshold_pass` bool,    -- does this detection pass some specified cuts?
`deprecated` bool,                -- option to ignore this detection
`realbogus_factor` float,         -- machine learning real/bogus value
PRIMARY KEY `key_id` (`id`),
UNIQUE KEY `key_tphot_id_expname` (`tphot_id`, `expname`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_ra_dec` (`ra`,`dec`),
KEY `idx_expname` (`expname`)
) ENGINE=InnoDB;
