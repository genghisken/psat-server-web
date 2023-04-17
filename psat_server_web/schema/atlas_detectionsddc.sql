drop table if exists `atlas_detectionsddc`;
--
-- atlas_detectionsddc.sql
-- Author: K. W. Smith
-- Initially created by generateATLASSchemaAndCPPClasses.py
-- on 2017-06-06
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
CREATE TABLE `atlas_detectionsddc` (
`id` bigint unsigned not null auto_increment,     -- autoincrementing detection id
`atlas_metadata_id` bigint(20) unsigned NOT NULL, -- a reference to the input file and other information (OBS data)
`atlas_object_id` bigint(20) unsigned NOT NULL,   -- a reference to the unique object which tags this object
`det_id` int unsigned not null,                   -- the internal id of the detection (unique per file)
`ra` double, 
`dec` double, 
`mag` float, 
`dmag` float, 
`x` float, 
`y` float, 
`major` float, 
`minor` float, 
`phi` float, 
`det` tinyint, 
`chin` float, 
`pvr` smallint, 
`ptr` smallint, 
`pmv` smallint, 
`pkn` smallint, 
`pno` smallint, 
`pbn` smallint, 
`pcr` smallint, 
`pxt` smallint, 
`psc` smallint, 
`dup` tinyint, 
`wpflx` float, 
`dflx` float, 
`date_modified` datetime,            -- when was the detection modified?
`image_group_id` bigint unsigned, -- a reference to the group of images that refers to this detection
`quality_threshold_pass` bool,    -- does this detection pass some specified cuts?
`deprecated` bool,                -- option to ignore this detection
`realbogus_factor` float,         -- machine learning real/bogus value
`htm16ID` bigint unsigned,
`date_inserted` datetime NOT NULL,   -- when was the detection inserted?
PRIMARY KEY `key_id` (`id`),
KEY `idx_atlas_object_id` (`atlas_object_id`),
KEY `idx_atlas_metadata_id` (`atlas_metadata_id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_date_inserted` (`date_inserted`),
KEY `idx_ra_dec` (`ra`,`dec`)
) ENGINE=InnoDB;
