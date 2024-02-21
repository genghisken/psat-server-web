-- 2024-01-17 KWS New virtual research assistant probabilities table.
drop table if exists `tcs_vra_probabilities`;

create table `tcs_vra_probabilities` (
`id` bigint unsigned not null auto_increment,  -- autoincrementing detection id
`transient_object_id` bigint(20) unsigned NOT NULL,
`preal` float,
`pgal` float,
`pfast` float,
`timestamp` timestamp not null default current_timestamp,
`apiusername` varchar(30) default null,
`username` varchar(30) default null,
`debug` bool not null default false,
primary key `idx_pk_id` (`id`),
key `idx_transient_object_id` (`transient_object_id`)
) engine=InnoDB;
