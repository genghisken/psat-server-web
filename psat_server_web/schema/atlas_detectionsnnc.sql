CREATE TABLE `atlas_detectionsnnc` (
`id` bigint unsigned not null auto_increment,     -- autoincrementing detection id
`atlas_metadata_id` bigint(20) unsigned NOT NULL, -- a reference to the input file and other information (OBS data)
`atlas_object_id` bigint(20) unsigned NOT NULL,   -- a reference to the unique object which tags this object
`detection_id` bigint(20) unsigned,               -- reference to the ddc detection ID
`det_id` int unsigned not null,                   -- the internal id of the detection (unique per file)
`ra` double, 
`dec` double, 
`mag` float, 
`dmag` float, 
`x` float, 
`y` float, 
`elong` float, 
`minor` float, 
`phi` float, 
`det` tinyint, 
`chin` float, 
`real` float, 
`var` float, 
`lin` float, 
`flaw` float, 
`cr` float, 
`prat` float, 
`mrat` float, 
`tail` float, 
`tphi` smallint unsigned, 
`lphi` smallint unsigned, 
`flg` smallint unsigned, 
`wpflux` float, 
`dwpflx` float, 
`grp` smallint unsigned, 
`nnc_id` varchar(30), 
`date_modified` datetime,            -- when was the detection modified?
`image_group_id` bigint unsigned,    -- a reference to the group of images that refers to this detection
`quality_threshold_pass` bool,       -- does this detection pass some specified cuts?
`deprecated` bool,                   -- option to ignore this detection
`realbogus_factor` float,            -- machine learning real/bogus value
`htm16ID` bigint unsigned,
`date_inserted` datetime NOT NULL,   -- when was the detection inserted?
PRIMARY KEY `key_id` (`id`),
KEY `idx_atlas_object_id` (`atlas_object_id`),
KEY `idx_atlas_metadata_id` (`atlas_metadata_id`),
KEY `idx_detection_id` (`detection_id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_date_inserted` (`date_inserted`),
KEY `idx_ra_dec` (`ra`,`dec`)
) ENGINE=InnoDB;
