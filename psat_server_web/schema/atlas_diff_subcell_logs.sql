-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).

drop table if exists `atlas_diff_subcell_logs`;

create table `atlas_diff_subcell_logs` (
`id` bigint unsigned not null auto_increment,
`obs` varchar(60),
`cnv` varchar(10),
`region` smallint unsigned,
`x1` smallint unsigned,
`x2` smallint unsigned,
`y1` smallint unsigned,
`y2` smallint unsigned,
`nstamp` smallint unsigned,
`trim` smallint unsigned,
`sumkern` float,
`sigstmp1` float,
`avscat` float,
`sigstmp2` float,
`fscat` float,
`goodrat` float,
`okrat` float,
`x2norm` float,
`diffrat` float,
PRIMARY KEY `pk_id` (`id`),
UNIQUE KEY `idx_obs_region` (`obs`, `region`),
KEY `idx_obs` (`obs`),
KEY `idx_region` (`region`)
) ENGINE=InnoDB;
