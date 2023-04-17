-- Table to contain all zooniverse scores. 
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_zooniverse_scores`;

create table `tcs_zooniverse_scores` (
`id` bigint unsigned not null auto_increment,
`transient_object_id` bigint(20) unsigned NOT NULL,
`score` float NOT NULL,
`user1` varchar(128) default null,
`user2` varchar(128) default null,
`user3` varchar(128) default null,
`date_inserted` datetime not null,
primary key `idx_pk_id` (`id`),
unique key `idx_transient_object_id` (`transient_object_id`),
key `idx_date_inserted` (`date_inserted`)
) engine=InnoDB;
