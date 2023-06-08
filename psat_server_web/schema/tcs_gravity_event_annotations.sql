-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
-- 2023-05-11 KWS Added timedelta, which is calculated by skytag. We can calculate it
--                by joining to the tcs_gravity_events table (assuming the entry exists)
--                but since skytag already calculates it, why not just use it.
drop table if exists tcs_gravity_event_annotations;

CREATE TABLE `tcs_gravity_event_annotations` (
  `primaryId` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `transient_object_id` bigint(20) unsigned NOT NULL,
  `gravity_event_id` varchar(10) COLLATE utf8_swedish_ci NOT NULL,
  `gracedb_id` varchar(10) COLLATE utf8_swedish_ci NOT NULL,
  `enclosing_contour` int(11) DEFAULT NULL,
  `map_name` varchar(100) COLLATE utf8_swedish_ci DEFAULT NULL,
  `map_iteration` varchar(100) DEFAULT NULL,
  `days_since_event` float DEFAULT NULL,
  `probability` float DEFAULT NULL,
  `distance` float DEFAULT NULL,
  `distance_sigma` float DEFAULT NULL,
  `dateLastModified` datetime DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateCreated` datetime DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  KEY `key_transient_object_id` (`transient_object_id`),
  UNIQUE `key_transient_gracedb_iteration` (`transient_object_id`, `gravity_event_id`, `map_iteration`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
