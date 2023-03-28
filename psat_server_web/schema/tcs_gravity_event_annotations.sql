drop table if exists tcs_gravity_event_annotations;

CREATE TABLE `tcs_gravity_event_annotations` (
  `primaryId` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `transient_object_id` bigint(20) unsigned NOT NULL,
  `gravity_event_id` varchar(10) COLLATE utf8_swedish_ci NOT NULL,
  `gracedb_id` varchar(10) COLLATE utf8_swedish_ci NOT NULL,
  `enclosing_contour` int(11) DEFAULT NULL,
  `map_name` varchar(30) COLLATE utf8_swedish_ci DEFAULT NULL,
  `dateLastModified` datetime DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateCreated` datetime DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  KEY `key_transient_object_id` (`transient_object_id`),
  UNIQUE KEY `transient_gracedb` (`transient_object_id`,`gracedb_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
