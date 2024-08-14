-- 2024-01-17 KWS New virtual research assistant scores table.
drop table if exists `tcs_vra_scores`;

create table `tcs_vra_scores` (
`id` bigint unsigned not null auto_increment,  -- autoincrementing detection id
`transient_object_id` bigint(20) unsigned NOT NULL,
`preal` float,
`pgal` float,
`pfast` float,
`rank_oxqub` float,
`rank_alt1` float,
`rank_alt2` float,
`timestamp` timestamp not null default current_timestamp,
`apiusername` varchar(30) default null,
`username` varchar(30) default null,
`debug` bool not null default false,
primary key `idx_pk_id` (`id`),
key `idx_transient_object_id` (`transient_object_id`)
) engine=InnoDB;
