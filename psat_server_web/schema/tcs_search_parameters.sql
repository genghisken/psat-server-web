--
--  Search Parameters - defines a group of parameters
--
--
-- 2009-10-01 KWS/DRY Added new parameter set
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_search_parameters`;

create table `tcs_search_parameters` (
`id` int unsigned not null,
`parameter_set_name` varchar(20) not null,
`comments` varchar(80),
`last_updated` datetime,
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_search_parameters (id, parameter_set_name, comments, last_updated)
values
(1, 'QUB TCS Version 1', 'First parameter set', NULL),
(2, 'QUB TCS Version 2', 'Changed NED parameters', '2009-10-01 10:00'),
(3, 'QUB TCS Version 3', 'Altered various parameters for MD searches', '2009-11-05 16:00');
