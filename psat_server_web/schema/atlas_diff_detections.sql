-- Table to facilitate rapid crossmatching of tphot detections.
-- Created to speed up crossmatching of fake sources injected into
-- ATLAS images.

-- The tphot header look like this (with ra, dec and mag added by Brian's code):
-- x        y     peakval  skyval  peakfit   dpeak  skyfit     flux     dflux    major  minor    phi  err chi/N ra dec mag mjd filter exptime zp htm14
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `atlas_diff_detections`;

create table `atlas_diff_detections` (
`id` bigint unsigned not null auto_increment,     -- autoincrementing detection id
`atlas_metadata_id` bigint(20) unsigned NOT NULL, -- a reference to the input file and other information (OBS data)
`atlas_object_id` bigint(20) unsigned NOT NULL,   -- a reference to the unique object which tags this object
`tphot_id` int unsigned not null,                 -- the internal id of the detection (unique per file)
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
-- 20151208 KWS New columns for DDT files BEGIN
`dm` float,
`peak` float,
`sky` float,
`varkrn` float,
`pstar` float,
`pkast` float,
`preal` float,
`star` int,
`dstar` int,
`mstar` float,
`kast` int,
`dkast` int,
-- 20151208 KWS New columns for DDT files END
`htm16ID` bigint unsigned not null,
`jtindex` int unsigned,
`date_inserted` datetime NOT NULL,   -- when was the detection inserted?
`date_modified` datetime,            -- when was the detection modified?
`image_group_id` bigint unsigned, -- a reference to the group of images that refers to this detection
`quality_threshold_pass` bool,    -- does this detection pass some specified cuts?
`deprecated` bool,                -- option to ignore this detection
`realbogus_factor` float,         -- machine learning real/bogus value
PRIMARY KEY `key_id` (`id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_atlas_object_id` (`atlas_object_id`),
KEY `idx_atlas_metadata_id` (`atlas_metadata_id`),
KEY `idx_tphot_id` (`tphot_id`),
KEY `idx_date_inserted` (`date_inserted`),
KEY `idx_ra_dec` (`ra`,`dec`)
) ENGINE=InnoDB;
