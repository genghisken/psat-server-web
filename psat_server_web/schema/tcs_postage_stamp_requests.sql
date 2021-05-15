--
--  Postage Stamp Requests
--
--  Stores the list of postage stamp requests sent to the postage stamp server
--
drop table if exists `tcs_postage_stamp_requests`;

create table `tcs_postage_stamp_requests` (
`id` bigint unsigned not null auto_increment,
`name` varchar(80) not null,
`pss_id` bigint unsigned,
`download_attempts` smallint unsigned not null,
`status` smallint unsigned not null,
`created` datetime not null,
`updated` datetime,
`request_type` smallint unsigned,
PRIMARY KEY `pk_id` (`id`),
UNIQUE KEY `idx_name` (`name`)
) ENGINE=MyISAM;

