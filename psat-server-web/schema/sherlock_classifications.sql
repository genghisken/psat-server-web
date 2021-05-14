drop table if exists sherlock_classifications;

CREATE TABLE `sherlock_classifications` (
  `transient_object_id` bigint(20) NOT NULL,
  `classification` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `annotation` text COLLATE utf8_unicode_ci,
  `summary` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `matchVerified` tinyint(4) DEFAULT NULL,
  `developmentComment` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `dateLastModified` datetime DEFAULT NULL,
  `dateCreated` datetime DEFAULT NULL,
  `updated` varchar(45) COLLATE utf8_unicode_ci DEFAULT '0',
  `separationArcsec` double DEFAULT NULL,
  PRIMARY KEY (`transient_object_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
