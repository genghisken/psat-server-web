-- The ATLAS non-diff objects table.  This table is used to tag all detections
-- with an object id.  The equivalent atlas_detections table, although created
-- for MySQL will eventually just be a "big data" flat table.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `atlas_objects`;

create table `atlas_objects` (
`id` bigint unsigned not null,        -- the unique object id (19 digit number) with which to tag all detections (PK)
`detection_id` int unsigned not null, -- the internal id of the detection used to create this ID (FK)
`ra` double not null,
`dec` double not null,
`htm16ID` bigint unsigned not null,
`jtindex` int unsigned,
`images_id` bigint(20) unsigned,      -- a reference to the most recent quickview images
`date_inserted` datetime NOT NULL,    -- when was the row inserted?
`date_modified` datetime,             -- when was the row modified?
`processing_flags` int unsigned,
`updated_by` varchar(40),
`realbogus_factor` float,             -- machine learning real/bogus value
`current_trend` varchar(40),
`observation_status` varchar(40),
`object_classification` int unsigned, -- what does the context classifier think the object is?
`followup_priority` int unsigned,
`external_reference_id` varchar(40),
`followup_id` int unsigned,
`detection_list_id` smallint unsigned, -- what list is the object in? e.g. eyeball, good, garbage
`followup_flag_date` date,             -- when did we flag the object?
`survey_field` varchar(10),
`followup_counter` int unsigned,       -- used to give the object an internal name
`atlas_designation` varchar(40),
`other_designation` varchar(40),
`ndetections` int unsigned,            -- a counter for the number of detections (for innodb use)
PRIMARY KEY `key_id` (`id`),
KEY `idx_detection_id` (`detection_id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_ra_dec` (`ra`,`dec`)
) ENGINE=InnoDB;
