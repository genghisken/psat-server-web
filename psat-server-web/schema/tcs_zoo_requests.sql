--
--  Supernova Zoo Image Triplet uploader tracker
--
--  Stores the candidate batch that has been sent the supernova zoo
--  Note that it's not yet clear how the zoo submission will work
--       but we need to keep track of which candidates have been
--       sent to the zoo.
--
drop table if exists `tcs_zoo_requests`;

create table `tcs_zoo_requests` (
`id` bigint unsigned not null auto_increment,
`name` varchar(80) not null,
`zoo_id` bigint unsigned,
`download_attempts` smallint unsigned not null,
`status` smallint unsigned not null,
`created` datetime not null,
`updated` datetime,
PRIMARY KEY `pk_id` (`id`),
UNIQUE KEY `idx_name` (`name`)
) ENGINE=MyISAM;

