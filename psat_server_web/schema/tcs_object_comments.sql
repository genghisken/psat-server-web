-- Table to contain all object comments.  Allows multiple users to add comments and allows comments to be tracked.
-- 2017-05-09 Make sure that comments cannot be added more than once. Index added for migration purposes.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_object_comments`;

create table `tcs_object_comments` (
`id` bigint unsigned not null auto_increment,  -- autoincrementing detection id
`transient_object_id` bigint(20) unsigned NOT NULL,
`comment` varchar(255) default null,
`date_inserted` datetime not null,    -- when was the row inserted?
`username` varchar(30) default null,
primary key `idx_pk_id` (`id`),
key `idx_transient_object_id` (`transient_object_id`),
unique key `idx_toid_di_un` (`transient_object_id`, `date_inserted`,`username`)
) engine=InnoDB;
