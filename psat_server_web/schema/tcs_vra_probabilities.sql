-- 2024-01-17 KWS New virtual research assistant probabilities table.
drop table if exists `tcs_vra_probabilities`;

create table `tcs_vra_probabilities` (
`id` bigint unsigned not null auto_increment,  -- autoincrementing detection id
`transient_object_id` bigint(20) unsigned NOT NULL,
`preal` float,
`pgal` float,
`pfast` float,
`updated` timestamp not null default current_timestamp,
`deprecated` bool not null default false,
`username` varchar(30) default null,
primary key `idx_pk_id` (`id`),
key `idx_transient_object_id` (`transient_object_id`),
unique key `idx_transient_object_id_deprecated` (`transient_object_id`, `deprecated`)
) engine=InnoDB;
