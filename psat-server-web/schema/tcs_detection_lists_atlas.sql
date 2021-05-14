--
--  Detection Lists
--
--
drop table if exists `tcs_detection_lists`;

create table `tcs_detection_lists` (
`id` smallint unsigned not null,
`name` varchar(20) not null,
`description` varchar(80),
PRIMARY KEY `pk_id` (`id`)
) ENGINE=MyISAM;

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

