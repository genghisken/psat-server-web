--
-- 2013-05-28 KWS Completely re-puropsed the tcs_images table to
--                show a representative row of objects.  In the first
--                instance, this will be the most recent row of images.
--                Note that the target image is mandatory, but the rest
--                are not.  This facilitates FGSS where only the target
--                image is actually shown.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
--
drop table if exists `tcs_images`;

create table `tcs_images` (
`id` bigint unsigned not null auto_increment,
`target` varchar(255) not null,
`ref` varchar(255),
`diff` varchar(255),
`mjd_obs` double not null,
PRIMARY KEY `pk_id` (`id`),
KEY `idx_target` (`target`),
KEY `idx_ref` (`ref`),
KEY `idx_diff` (`diff`),
KEY `idx_mjd_obs` (`mjd_obs`)
) ENGINE=InnoDB;

