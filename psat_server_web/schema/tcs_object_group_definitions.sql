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
('PSSTTargets', 'PSST Observation Targets'),
('PS2Test', 'PS2 Test Targets'),
('DiscoveryATel', 'Discovery ATel Objects'),
('Ken', 'Ken''s Objects'),
('Heather', 'Heather''s Objects'),
('Mark', 'Mark''s Targets'),
('QUBConfSNeIa', 'QUB confirmed SNe Ia'),
('HotChip', 'Hot GPC1 OTA Investigation'),
('HotChipGood', 'HOT GPC1 OTA Investigation - possible good objects'),
('NT', 'Nuclear Transients'),
('watch', 'Recent Object Watch List'),
('lowz', 'Low z SN List'),
('Dipoles', 'Dipole Examples'),
('BadSubExamples', 'General Bad Subtraction Examples'),
('Cosimo', 'Cosimo''s Objects'),
('Darryl', 'Darryl''s Objects'),
('Dave', 'Dave''s Objects'),
('Janet', 'Janet''s Objects'),
('Peter', 'Peter''s Objects (MSci)'),
('Giacomo', 'Giacomo''s Objects'),
('Matt', 'Matt''s Objects'),
('Morgan', 'Morgan''s Objects'),
('Rubina', 'Rubina''s Objects'),
('Stephen', 'Stephen''s Objects'),
('Kuki', 'Kuki''s Objects'),
('Ghosts', 'Ghost and Crosstalk Investigation'),
('Fast', 'PC: Fast'),
('Medium', 'PC: Medium'),
('CVs', 'PC: CVs'),
('Dean', 'Dean''s objects (MSci)');



-- +----+----------------------+--------------------------------------+
-- | id | name                 | description                          |
-- +----+----------------------+--------------------------------------+
-- |  1 | ObservationTargets   | Current Observation Targets          | 
-- |  2 | MattOrphans          | Matt's Orphans                       | 
-- |  3 | MattFHOrphans        | Matt's Faint Host Orphans            | 
-- |  4 | Talks                | Publicity Objects - Useful for Talks | 
-- |  5 | Convolution          | Single Convolution Issues            | 
-- |  6 | Ken                  | Ken's Objects                        | 
-- |  7 | Heather              | Heather's Objects                    | 
-- |  8 | OldDiffImagesMissing | Older Diff Images Missing            | 
-- |  9 | QUBConfSNeIa         | QUB confirmed SNe Ia                 | 
-- +----+----------------------+--------------------------------------+

