-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--     Obs      <sumkern> srms  <good> grms nbad  badcells        B K   nddc  freal fvar  ftran fdup
-- 01a58543o0002o   0.980 0.018  2.054 0.405   0 0000000000000000 0 1    3265 0.178 0.007 0.171 0.037

drop table if exists `atlas_diff_logs`;

create table `atlas_diff_logs` (
`id` bigint unsigned not null auto_increment,
`obs` varchar(60),
`sumkern` float,
`srms` float,
`good` float,
`grms` float,
`nbad` tinyint unsigned,
`badcells` bigint unsigned,
`b` tinyint unsigned,
`k` tinyint unsigned,
`nddc` int unsigned,
`freal` float,
`fvar` float,
`ftran` float,
`fdup` float,
PRIMARY KEY `pk_id` (`id`),
UNIQUE KEY `idx_obs` (`obs`)
) ENGINE=InnoDB;
