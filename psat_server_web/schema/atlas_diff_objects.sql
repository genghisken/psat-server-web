-- Table to facilitate rapid crossmatching of tphot detections.
-- Created to speed up crossmatching of fake sources injected into
-- ATLAS images.

-- Unlike in Pan-STARRS, we will store ALL the detections in the detections table
-- (hence no nasty table joins, etc).

-- With some minor modifications in the HTM code we should no longer need the cx, cy, cz columns.

-- 2015-12-02 KWS Added three new composite indexes in an attempt to improve web page
--                responsiveness. Also added key to detection_list_id.
-- 2016-04-14 KWS Added new keys to atlas_designation and other_designation
-- 2016-07-07 KWS Added zooniverse_score and sherlockClassification.
-- 2018-06-21 KWS The detection_id column needs to be bigint unsigned! Otherwise after 4 billion
--                detections inserts into this table will FAIL!
-- 2018-06-21 KWS Changed the followup_flag_date to datetime, rather than date.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `atlas_diff_objects`;

create table `atlas_diff_objects` (
`id` bigint unsigned not null,        -- the unique object id (19 digit number) with which to tag all detections (PK)
`detection_id` bigint unsigned not null, -- the internal id of the detection used to create this ID (FK)
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
`followup_flag_date` datetime,         -- when did we flag the object?
`survey_field` varchar(10),
`followup_counter` int unsigned,       -- used to give the object an internal name
`atlas_designation` varchar(40),
`other_designation` varchar(40),
`local_comments` varchar(255),         -- a local comments table.  Will be moved to an external table.
`ndetections` int unsigned,            -- a counter for the number of detections (for innodb use)
`zooniverse_score` float,
`sherlockClassification` varchar(40),
PRIMARY KEY `key_id` (`id`),
KEY `idx_detection_id` (`detection_id`),
KEY `idx_htm16ID` (`htm16ID`),
KEY `idx_ra_dec` (`ra`,`dec`),
KEY `idx_fu_id` (`followup_id`),
KEY `idx_fu_flag_date` (`followup_flag_date`),
KEY `idx_fu_counter` (`followup_counter`),
KEY `idx_survey_field` (`survey_field`),
KEY `idx_detection_list` (`detection_list_id`),
KEY `idx_date_inserted` (`date_inserted`),
KEY `idx_atlas_designation` (`atlas_designation`),
KEY `idx_other_designation` (`other_designation`),
KEY `idx_detection_list_id_object_classification` (detection_list_id, object_classification),
KEY `idx_detection_list_id_observation_status` (detection_list_id, observation_status),
KEY `idx_detection_list_id_realbogus_factor` (detection_list_id, realbogus_factor)
) ENGINE=InnoDB;
