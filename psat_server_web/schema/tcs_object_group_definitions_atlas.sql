--
--  Detection Lists
--
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_object_group_definitions`;

create table `tcs_object_group_definitions` (
`id` smallint unsigned not null auto_increment,
`name` varchar(20) not null,
`description` varchar(80),
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_object_group_definitions (name, description)
values
('ObservationTargets', 'Current Observation Targets'),
('PESSTOTargets', 'PESSTO Observation Targets'),
('FastTrackAtel', 'Fast Track ATel Objects'),
('TNS', 'Transient Name Server Objects'),
('DiscoveryATel', 'Discovery ATel Objects'),
('Ken', 'Ken''s Objects'),
('Brian', 'Brian''s Objects'),
('Armin', 'Armin''s Targets'),
('Stephen', 'Stephen''s Objects'),
('Darryl', 'Darryl''s Objects'),
('Dave', 'Dave''s Objects'),
('John', 'John''s Objects'),
('Larry', 'Larry''s Objects'),
('Ari', 'Ari''s Objects'),
('KN', 'Kilonova Candidates'),
('GW2', 'G211117 List'),
('HPM', 'High Proper Motion Star Examples'),
('Ryan', 'Ryan''s Objects'),
('orphans', 'Orphan Investigation'),
('GW3', 'G268556 List'),
('G277583', 'G277583 List'),
('G274296', 'G274296 List'),
('G284239', 'G284239 List'),
('Janet', 'Janet''s Objects'),
('negative', 'Negative Flux in Input Images'),
('G296853', 'G296853 List'),
('G297595', 'G297595 List'),
('G298936', 'G298936 List'),
('G299232', 'G299232 List'),
('G298048', 'G298048 List'),
('Michael', 'Michael''s Objects'),
('Owen', 'Owen''s Objects'),
('Gavin', 'Gavin''s Objects'),
('K2C16', 'K2 Campaign 16 Targets'),
('K2C17', 'K2 Campaign 17 Targets'),
('David', 'David''s Objects'),
('Peter', 'Peter''s Objects'),
('Erkki', 'Erkki''s Objects'),
('Mark', 'Mark''s Objects'),
('CV', 'CV Candidates'),
('Christelle', 'Christelle''s Objects'),
('Simon', 'Simon''s Objects');
