--
-- IPP objects to CfA objects lookup table
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_ipp_to_cfa_lookup`;

create table `tcs_ipp_to_cfa_lookup` (
`transient_object_id` bigint unsigned not null,
`eventID` bigint unsigned,
`cfa_designation` varchar(15),
`separation` float,
PRIMARY KEY `pk_transient_object_id` (`transient_object_id`),
KEY `key_eventID` (`eventID`),
KEY `key_cfa_designation` (`cfa_designation`)
) ENGINE=InnoDB;

