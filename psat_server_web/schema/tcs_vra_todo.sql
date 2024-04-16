-- 2024-01-17 KWS New virtual research assistant scores table.
drop table if exists `tcs_vra_todo`;

create table `tcs_vra_todo` (
`transient_object_id` bigint(20) NOT NULL,
`timestamp` timestamp not null default current_timestamp,
primary key `idx_transient_object_id` (`transient_object_id`)
) engine=InnoDB;
