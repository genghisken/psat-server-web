-- 2024-01-17 KWS New virtual research assistant rank table.
drop table if exists `tcs_vra_rank`;

create table `tcs_vra_rank` (
`transient_object_id` bigint(20) NOT NULL,
`rank` float NOT NULL,
`rank_alt1` float NOT NULL,
`is_gal_cand` bool NOT NULL,
`timestamp` timestamp not null default current_timestamp,
primary key `idx_transient_object_id` (`transient_object_id`)
) engine=InnoDB;
