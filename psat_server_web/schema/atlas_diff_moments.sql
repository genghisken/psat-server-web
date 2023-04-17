-- Table to contain tphot moments (.mom) data.

-- The moments (.mom) header look like this:
-- x y cx cy xpk ypk rkron rvar flux crad qrad trad q2 q2cos q2sin q3cos q3sin q1cos q1sin
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `atlas_diff_moments`;

create table `atlas_diff_moments` (
`id` bigint unsigned not null auto_increment,  -- autoincrementing detection id
`detection_id` int unsigned not null, -- the internal id of the detection used to create this row (FK)
`x` float,
`y` float,
`cx` float,
`cy` float,
`xpk` float,
`ypk` float,
`rkron` float,
`rvar` float,
`flux` float,
`crad` float,
`qrad` float,
`trad` float,
`q2` float,
`q2cos` float,
`q2sin` float,
`q3cos` float,
`q3sin` float,
`q1cos` float,
`q1sin` float,
`date_inserted` datetime NOT NULL,   -- when was the row inserted?
`date_modified` datetime,            -- when was the row modified?
`realbogus_factor` float,            -- machine learning real/bogus value
PRIMARY KEY `key_id` (`id`),
KEY `idx_detection_id` (`detection_id`),
KEY `idx_realbogus_factor` (`realbogus_factor`),
KEY `idx_date_inserted` (`date_inserted`)
) ENGINE=InnoDB;
