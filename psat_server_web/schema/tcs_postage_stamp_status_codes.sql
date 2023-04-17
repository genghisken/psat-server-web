--
--  Postage Stamp Status Codes
--
--  Stores the list of postage stamp requests sent to the postage stamp server
--
-- 2011-11-11 KWS Minor modification of status codes to reflect current usage.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--

drop table if exists `tcs_postage_stamp_status_codes`;

create table `tcs_postage_stamp_status_codes` (
`id` smallint unsigned not null,
`code` varchar(20) not null,
`description` varchar(80),
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_postage_stamp_status_codes (id, code, description)
values
(0, 'created', 'Request has been created but not dispatched'),
(1, 'dispatched', 'Request has been dispatched'),
(2, 'complete', 'Request has been completed'),
(3, 'pending', 'Request is awaiting response'),
(4, 'timeout', 'Request was dispatched but no result has been created yet'),
(5, 'processing', 'Request is currently being processed'),
(6, 'missing', 'Request is missing'),
(7, 'failed', 'Request has failed');
