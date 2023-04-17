-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_followup_telescopes`;

create table `tcs_followup_telescopes` (
`id` smallint unsigned not NULL,
`name` varchar(30) not NULL,
`description` varchar(60) not NULL,
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_followup_telescopes (id, name, description)
values
(0, 'PS1', 'Pan-STARRS1'),
(1, 'WHT', 'William Herschel Telescope'),
(2, 'INT', 'Isaac Newton Telescope'),
(3, 'TNG', 'Telescopio Nazionale Galileo'),
(4, 'LT', 'Liverpool Telescope'),
(5, 'FTN', 'Faulkes North'),
(6, 'FTS', 'Faulkes South'),
(7, 'GN', 'Gemini North'),
(8, 'GS', 'Gemini South'),
(9, 'NOT', 'Nordic Optical Telescope'),
(10, 'NTT', 'New Technology Telescope');

