drop table if exists sherlock_classifications;

CREATE TABLE `sherlock_classifications` (
  `transient_object_id` bigint(20) NOT NULL,
  `classification` varchar(45) DEFAULT NULL,
  `annotation` text DEFAULT NULL,
  `summary` varchar(50) DEFAULT NULL,
  `matchVerified` tinyint(4) DEFAULT NULL,
  `developmentComment` varchar(100) DEFAULT NULL,
  `dateLastModified` datetime DEFAULT NULL,
  `dateCreated` datetime DEFAULT NULL,
  `updated` varchar(45) DEFAULT '0',
  `separationArcsec` double DEFAULT NULL,
  PRIMARY KEY (`transient_object_id`),
  KEY `idx_summary_transient_object_id` (`summary`,`transient_object_id`)
) ENGINE=InnoDB
;
