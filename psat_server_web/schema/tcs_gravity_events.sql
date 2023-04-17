-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists tcs_gravity_events;

CREATE TABLE `tcs_gravity_events` (
  `gravity_event_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `gracedb_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `mjd` double DEFAULT NULL,
  `dateLastModified` datetime DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateCreated` datetime DEFAULT NULL,
  PRIMARY KEY (`gravity_event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
