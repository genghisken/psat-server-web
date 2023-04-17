--
--  Classification Flag Values
--
-- 2010-01-28 KWS Added a Description field so that the web page titles
--                for each type of object can be database driven rather
--                than hard wired into the Web interface code.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_classification_flags`;

create table `tcs_classification_flags` (
`flag_id` smallint unsigned not null,
`flag_name` varchar(30) not null,
`description` varchar(80),
PRIMARY KEY `pk_flag_id` (`flag_id`)
) ENGINE=InnoDB;

insert into tcs_classification_flags (flag_id, flag_name, description)
values
(1, 'orphan', 'Orphan'),
(2, 'variablestar', 'Variable Star'),
(4, 'nt', 'Nuclear Transient'),
(8, 'agn', 'Active Galactic Nucleus'),
(16, 'sn', 'Supernova'),
(32, 'miscellaneous', 'Associated Orphan'),
(64, 'tde', 'Tidal Disruption Event'),
(128, 'lens', 'Lens'),
(256, 'mover', 'Mover'),
(512, 'bright', 'Bright'),
(1024, 'kepler', 'Kepler');
