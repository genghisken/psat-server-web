--
-- CfA objects to IPP objects lookup table
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_cfa_to_ipp_lookup`;

create table `tcs_cfa_to_ipp_lookup` (
`eventID` bigint unsigned not null,
`transient_object_id` bigint unsigned,
`cfa_designation` varchar(15),
`separation` float,
PRIMARY KEY `pk_eventID` (`eventID`),
KEY `key_transient_object_id` (`transient_object_id`),
KEY `key_cfa_designation` (`cfa_designation`)
) ENGINE=InnoDB;

