--
--  Parameter definitions
--
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_parameter_definitions`;

create table `tcs_parameter_definitions` (
`id` int unsigned not null,
`name` varchar(40) not null,
`type` varchar(20) not null,
`value` varchar(40) not null,
`units` varchar(40) not null,
`catalogue_table_id` smallint unsigned not null,
`search_parameters_id` int unsigned not null,
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_parameter_definitions(id, name, type, value, units, catalogue_table_id, search_parameters_id)
values
(1, 'LocalTransientsSearchRadius', 'double', '1.0', 'arcsec', 0, 1),
(2, 'VeronSearchRadius', 'double', '2.0', 'arcsec', 8, 1),
(3, '2MassXSCSearchRadius', 'double', '2.0', 'arcsec', 2, 1),
(4, 'SDSSStarsSearchRadius', 'double', '3.0', 'arcsec', 7, 1),
(5, '2MassPSCSearchRadius', 'double', '3.0', 'arcsec', 1, 1),
(6, 'GSCSearchRadius', 'double', '3.0', 'arcsec', 3, 1),
(7, 'NEDSearchRadius1', 'double', '50.0', 'arcmin', 4, 1),
(8, 'NEDRedshiftSearch', 'double', '35.0', 'kpc', 4, 1),
(9, 'NEDSearchRadius2', 'double', '2.0', 'arcsec', 4, 1),
(10, 'NEDSearchRadius3', 'double', '1.0', 'arcmin', 4, 1),
(11, 'SDSSGalaxiesSearchRadius1', 'double', '3.0', 'arcsec', 5, 1),
(12, 'SDSSGalaxiesSearchRadius2', 'double', '5.0', 'arcsec', 5, 1),
(13, 'LocalTransientsSearchRadius', 'double', '1.0', 'arcsec', 0, 2),
(14, 'VeronSearchRadius', 'double', '2.0', 'arcsec', 8, 2),
(15, '2MassXSCSearchRadius', 'double', '2.0', 'arcsec', 2, 2),
(16, 'SDSSStarsSearchRadius', 'double', '3.0', 'arcsec', 7, 2),
(17, '2MassPSCSearchRadius', 'double', '3.0', 'arcsec', 1, 2),
(18, 'GSCSearchRadius', 'double', '3.0', 'arcsec', 3, 2),
(19, 'NEDSearchRadius1', 'double', '14.0', 'arcmin', 4, 2),
(20, 'NEDRedshiftSearch', 'double', '15.0', 'kpc', 4, 2),
(21, 'NEDSearchRadius2', 'double', '2.0', 'arcsec', 4, 2),
(22, 'NEDSearchRadius3', 'double', '1.0', 'arcmin', 4, 2),
(23, 'SDSSGalaxiesSearchRadius1', 'double', '3.0', 'arcsec', 5, 2),
(24, 'SDSSGalaxiesSearchRadius2', 'double', '5.0', 'arcsec', 5, 2),
(25, 'LocalTransientsSearchRadius', 'double', '1.0', 'arcsec', 0, 3),
(26, 'VeronSearchRadius', 'double', '2.0', 'arcsec', 8, 3),
(27, '2MassXSCSearchRadius', 'double', '2.0', 'arcsec', 2, 3),
(28, 'SDSSStarsSearchRadius', 'double', '3.0', 'arcsec', 7, 3),
(29, '2MassPSCSearchRadius', 'double', '3.0', 'arcsec', 1, 3),
(30, 'GSCSearchRadius', 'double', '3.0', 'arcsec', 3, 3),
(31, 'NEDSearchRadius1', 'double', '6.0', 'arcsec', 4, 3),
(32, 'NEDRedshiftSearch', 'double', 'any', 'kpc', 4, 3),
(33, 'NEDSearchRadius2', 'double', '2.0', 'arcsec', 4, 3),
(34, 'NEDSearchRadius3', 'double', '1.0', 'arcmin', 4, 3),
(35, 'SDSSGalaxiesSearchRadius1', 'double', '3.0', 'arcsec', 5, 3),
(36, 'SDSSGalaxiesSearchRadius2', 'double', '6.0', 'arcsec', 5, 3);
