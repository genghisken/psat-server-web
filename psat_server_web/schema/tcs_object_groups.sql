-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_object_groups`;

create table `tcs_object_groups` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
`transient_object_id` bigint unsigned NOT NULL,
`object_group_id` smallint unsigned NOT NULL,
PRIMARY KEY `idx_id` (`id`),
KEY `idx_transient_object_id` (`transient_object_id`),
KEY `idx_object_group_id` (`object_group_id`),
UNIQUE KEY `idx_transient_object_id_object_group_id` (`transient_object_id`,`object_group_id`)
) ENGINE=InnoDB;
