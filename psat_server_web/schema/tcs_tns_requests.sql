--
--  Transient Nameserver Requests
--
--  Stores the list of tns requests sent to the transient name server
--
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_tns_requests`;

create table `tcs_tns_requests` (
`id` bigint unsigned not null auto_increment,
`tns_report_id` bigint unsigned,
`download_attempts` smallint unsigned not null,
`status` smallint unsigned not null,
`created` datetime not null,
`updated` datetime,
`request_type` smallint unsigned,
PRIMARY KEY `pk_id` (`id`),
UNIQUE KEY `idx_name` (`tns_report_id`)
) ENGINE=InnoDB;

