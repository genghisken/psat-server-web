--
--  Detection Lists
--
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_detection_lists`;

create table `tcs_detection_lists` (
`id` smallint unsigned not null,
`name` varchar(20) not null,
`description` varchar(80),
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_detection_lists (id, name, description)
values
(0, 'garbage', 'Bad Candidates'),
(1, 'confirmed', 'Confirmed SNe'),
(2, 'good', 'Good Candidates'),
(3, 'possible', 'Possible Candidates'),
(4, 'pending', 'Not Yet Eyeballed'),
(5, 'attic', 'Attic'),
(6, 'stars', 'Stars'),
(7, 'edge', 'Too close to the Edge'),
(8, 'cold', 'Cold Storage Area');

