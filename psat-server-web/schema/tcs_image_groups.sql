--
--  Image groups table.  This is a work in progress.  May need an
--  extra table to refer to the image metadata.  May also need
--  to refer to a general config table for things like "base directory"
--
--  Note that the 'name' is the transient_object_id + the mjd to three
--  or four truncated decimal places + the diff id.  Although the mjd
--  is not required for uniqueness, it helps users to know immediately
--  the age of the image (group).
--
drop table if exists `tcs_image_groups`;

create table `tcs_image_groups` (
`id` bigint unsigned not null auto_increment,
`name` varchar(255) not null,
`group_type` smallint unsigned,
PRIMARY KEY `pk_id` (`id`),
UNIQUE KEY `idx_name` (`name`)
) ENGINE=MyISAM;

