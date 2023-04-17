--
--  TCS Processing Status
--
--  Stores a flag for each time the TCS is started.  Allows a script
--  to know if the system is still running and thus abort the start
--  of the next run until it's complete. Only one row should ever have
--  a status that is not 'COMPLETED'.  Anything else means that it's
--  still running or that a fault has been encountered.
--
--  0 = STOPPED
--  1 = INGESTING
--  2 = CUTTING
--  3 = STATS
--  4 = TRENDS
--  5 = LIGHTCURVES
--  6 = RECURRENCEPLOTS
--  7 = LOCATIONMAPS
--  100 = COMPLETED
--  999 = FAULT
--
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_processing_status`;

create table `tcs_processing_status` (
`id` bigint unsigned not null auto_increment,
`status` smallint unsigned not null,
`started` datetime not null,
`modified` datetime,
PRIMARY KEY `pk_id` (`id`),
KEY `idx_started` (`started`),
KEY `idx_modified` (`modified`)
) ENGINE=InnoDB;

