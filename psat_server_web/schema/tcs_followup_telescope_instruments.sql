-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_followup_telescope_instruments`;

create table `tcs_followup_telescope_instruments` (
`id` smallint unsigned not NULL,
`telescope_id` smallint unsigned not NULL,
`name` varchar(30) not NULL,
`description` varchar(60) not NULL,
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_followup_telescope_instruments (id, telescope_id, name, description)
values
(0, 0, 'GPC1', 'Gigapixel-1'),
(1, 1, 'ACAM', 'Auxiliary-port CAMera'),
(2, 2, 'WFC', 'Wide Field Camera'),
(3, 3, 'DOLORES', 'Device Optimized for the LOw RESolution'),
(4, 4, 'RATCam', 'Robotic Astronomical Telescope Camera'),
(5, 5, 'EM01', 'FTN EM01'),
(6, 6, 'EM03', 'FTS EM03'),
(7, 7, 'GMOSN', 'Gemini Multi-Object Spectrograph N'),
(8, 8, 'GMOSS', 'Gemini Multi-Object Spectrograph S'),
(9, 9, 'ALFOSC', 'Andalucia Faint Object Spectrograph and Camera'),
(10, 10, 'EFOSC2', 'ESO Faint Object Spectrograph and Camera 2');

