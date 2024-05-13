-- 2023-06-15 KWS Added an "interesting" column - human override of alert significance

DROP TABLE `tcs_gravity_alerts`;

CREATE TABLE `tcs_gravity_alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `superevent_id` varchar(20) NOT NULL,
  `significant` tinyint(4) DEFAULT NULL,
  `alert_type` varchar(20) DEFAULT NULL,
  `alert_time` datetime DEFAULT NULL,
  `mjd_obs` double DEFAULT NULL,
  `far` double DEFAULT NULL,
  `distmean` float DEFAULT NULL,
  `diststd` float DEFAULT NULL,
  `class_bbh` float DEFAULT NULL,
  `class_bns` float DEFAULT NULL,
  `class_nsbh` float DEFAULT NULL,
  `class_terrestrial` float DEFAULT NULL,
  `prop_hasns` float DEFAULT NULL,
  `prop_hasremnant` float DEFAULT NULL,
  `prop_hasmassgap` float DEFAULT NULL,
  `area10` float DEFAULT NULL,
  `area50` float DEFAULT NULL,
  `area90` float DEFAULT NULL,
  `creator` varchar(30) DEFAULT NULL,
  `group` varchar(100) DEFAULT NULL,
  `pipeline` varchar(100) DEFAULT NULL,
  `map_iteration` varchar(100),
  `map` varchar(400) DEFAULT NULL,
  `interesting` tinyint(4) DEFAULT NULL,
  `dateAdded` datetime DEFAULT CURRENT_TIMESTAMP,
  `dateLastModified` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `superevent_id_alert_time_alert_type` (`superevent_id`,`alert_time`,`alert_type`)
) ENGINE=InnoDB
;
