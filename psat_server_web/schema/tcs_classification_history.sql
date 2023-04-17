--
--  Classification Flag Values
--
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_classification_history`;

create table `tcs_classification_history` (
`id` bigint unsigned not null auto_increment,
`transient_object_id` bigint unsigned not null,
`last_classification` smallint unsigned not null,
`reclassification_date` datetime not null,
`comments` varchar(255),
PRIMARY KEY `id` (`id`)
) ENGINE=InnoDB;
