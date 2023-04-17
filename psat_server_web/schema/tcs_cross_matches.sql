--
-- Link the Transient Object to the Catalogue which was used to categorise it.
--
-- transient_object_id - FK reference to unique transient in tcs_transient_objects.
--                       Note that since an object can be multiply classified, this
--                       must NOT be made a unique key in this table.
-- catalogue_object_id - Varchar reference (not enforceable) to catalogue primary key
-- catalogue_table_id - FK reference to tcs_catalogue_tables (identifies the catalogue
--                      to which the above reference belongs)
-- search_parameters_id - FK reference to tcs_search_parameters.  Identifies what group
--                        of parameters was used to classify this object.
-- separation - Distance (in arcsec) from transient to source in catalogue.
--
-- KWS0001 2009-07-31  Had to add primary key because web framework demands it.
--                     (Web framework does not support composite primary keys.)
--
-- 2010-11-11 KWS Added new "association_type" column.  Allows different types of cross-
--                matching to be recorded (e.g. closest object to ps1 object (1), closest
--                object to closest matched object (2), etc)
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `tcs_cross_matches`;

create table `tcs_cross_matches` (
`transient_object_id` bigint unsigned NOT NULL,
`catalogue_object_id` varchar(30) NOT NULL,
`catalogue_table_id` smallint unsigned NOT NULL,
`search_parameters_id` tinyint unsigned NOT NULL,
`separation` double,
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT, -- KWS0001
`z` double,
`scale` double,
`distance` double,
`distance_modulus` double,
`association_type` tinyint unsigned,
PRIMARY KEY `key_id` (`id`),
KEY `key_transient_object_id` (`transient_object_id`),
KEY `key_catalogue_object_id` (`catalogue_object_id`),
KEY `idx_separation` (`separation`)
) ENGINE=InnoDB;
