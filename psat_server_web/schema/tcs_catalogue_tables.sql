--
--  List of Catalogue Tables
--
-- 2010-11-11 KWS Added new tcs_cat_sdss_stars_galaxies table
--                (Combined SDSS stars & galaxies).
--
-- 2012-12-18 KWS Added the new SDSS DR9 catalogues, plus ROSAT,
--                CfA PS1 detections, and PESSTO transientBucket
--                and views.
-- 2023-04-17 KWS Switched to using InnoDB as backend. Requires the database to be small or
--                regularly purged (as has been done with ATLAS).
drop table if exists `tcs_catalogue_tables`;

create table `tcs_catalogue_tables` (
`id` smallint unsigned not NULL,
`table_name` varchar(40) not NULL,
`description` varchar(60) not NULL,
`url` varchar(255),
PRIMARY KEY `pk_id` (`id`)
) ENGINE=InnoDB;

insert into tcs_catalogue_tables (id, table_name, description, url)
values
(0, 'tcs_transient_objects', 'PS1 Transient Objects', NULL),
(1, 'tcs_2mass_psc_cat', '2MASS Point Source Catalogue', NULL),
(2, 'tcs_2mass_xsc_cat', '2MASS Extended Source Catalogue', NULL),
(3, 'tcs_guide_star_cat','Guide Star Catalogue 2.3', NULL),
(4, 'tcs_ned_cat','NASA Extragalactic Database', NULL),
(5, 'tcs_sdss_galaxies_cat','SDSS Photometric Galaxies DR7', 'http://cas.sdss.org/astrodr7/en/tools/explore/obj.asp'),
(6, 'tcs_sdss_spect_galaxies_cat','SDSS Spectroscopic Galaxies DR7', 'http://cas.sdss.org/astrodr7/en/tools/explore/obj.asp'),
(7, 'tcs_sdss_stars_cat','SDSS Photometric Stars', 'http://cas.sdss.org/astrodr7/en/tools/explore/obj.asp'),
(8, 'tcs_veron_cat','Veron AGN v12', NULL),
(9, 'tcs_cat_deep2dr3','Deep 2 DR 3', NULL),
(10, 'tcs_cat_md01_ned','MD01 NED Subset', NULL),
(11, 'tcs_cat_md02_ned','MD02 NED Subset', NULL),
(12, 'tcs_cat_md03_ned','MD03 NED Subset', NULL),
(13, 'tcs_cat_md04_ned','MD04 NED Subset', NULL),
(14, 'tcs_cat_md05_ned','MD05 NED Subset', NULL),
(15, 'tcs_cat_md06_ned','MD06 NED Subset', NULL),
(16, 'tcs_cat_md07_ned','MD07 NED Subset', NULL),
(17, 'tcs_cat_md08_ned','MD08 NED Subset', NULL),
(18, 'tcs_cat_md09_ned','MD09 NED Subset', NULL),
(19, 'tcs_cat_md10_ned','MD10 NED Subset', NULL),
(20, 'tcs_cat_md01_chiappetti2005','Chiappetti 2005', NULL),
(21, 'tcs_cat_md01_pierre2007','Pierre 2007', NULL),
(22, 'tcs_cat_md02_giacconi2002','Giacconi 2002', NULL),
(23, 'tcs_cat_md02_lefevre2004','LeFevre 2004', NULL),
(24, 'tcs_cat_md02_lehmer2005','Lehmer 2005', NULL),
(25, 'tcs_cat_md02_virani2006','Virani 2006', NULL),
(26, 'tcs_cat_md04_hasinger2007','Hasinger 2007', NULL),
(27, 'tcs_cat_md04_trump2007','Trump 2007', NULL),
(28, 'tcs_cat_md05_brunner2008','Brunner 2008', NULL),
(29, 'tcs_cat_md07_laird2009','Laird 2009', NULL),
(30, 'tcs_cat_md07_nandra2005','Nandra 2005', NULL),
(31, 'tcs_cat_md08_manners2003','Manners 2003', NULL),
(32, 'tcs_cat_sdss_stars_galaxies','SDSS Stars & Galaxies DR7', 'http://cas.sdss.org/astrodr7/en/tools/explore/obj.asp'),
(33, 'tcs_cat_sdss_lrg','SDSS Luminious Red Galaxies DR8', NULL),
(34, 'tcs_cat_slacs','Sloan Lenses in ACS', NULL),
(35, 'tcs_cat_milliquas','Million Quasars 2.7', 'http://quasars.org/milliquas.htm'),
(36, 'tcs_cat_sdss_dr9_photo_stars_galaxies','SDSS Stars & Galaxies DR9', 'http://skyserver.sdss3.org/public/en/tools/explore/obj.asp'),
(37, 'tcs_cat_sdss_dr9_spect_galaxies_qsos','SDSS Spectroscopic Galaxies & QSOs DR9', 'http://skyserver.sdss3.org/public/en/tools/explore/obj.asp'),
(38, 'tcs_cat_rosat_faint_1x29','ROSAT Faint Sources', NULL),
(39, 'tcs_cat_rosat_bright_1x10a','ROSAT Bright Sources', NULL),
(40, 'tcs_cfa_detections','CfA PS1 Detection Catalogue', NULL),
(41, 'tcs_cat_ps1_medium_deep_ref','PS1 Medium Deep Reference Catalogue', NULL),
(42, 'tcs_cat_kepler_k2','Kepler 2 Campaign Galaxies', NULL),
(43, 'tcs_cat_ps1_ubercal_stars','PS1 Ubercal Star Catalogue', NULL),
(44, 'tcs_cat_gaia_dr1','Gaia DR1', 'http://gea.esac.esa.int/archive/'),
(1000, 'transientBucket','The PESSTO Transient Objects', NULL),
(1001, 'view_transientBucketMaster','The PESSTO Transient Objects - primary object', NULL),
(1002, 'atel_coordinates','ATEL References', NULL),
(1003, 'fs_chase','CHASE Survey', NULL),
(1004, 'view_fs_crts_css_summary','CRTS - Catalina Sky Survey', NULL),
(1005, 'view_fs_crts_mls_summary','CRTS - Mount Lemmon Survey', NULL),
(1006, 'view_fs_crts_sss_summary','CRTS - Siding Spring Survey', NULL),
(1007, 'view_fs_lsq_summary','La Silla Quest Survey', NULL),
(1008, 'view_fs_ogle_summary','OGLE Survey', NULL),
(1009, 'cbats','CBATS', NULL),
(1010, 'view_cbats_sn','CBATS Supernovae', NULL),
(1011, 'view_cbats_psn','CBATS PSN List', NULL),
(1012, 'fs_brightsnlist_discoveries','Bright Supernova List', NULL),
(1013, 'fs_asassn_sne','ASASSN Supernovae', NULL),
(1014, 'fs_asassn_transients','ASASSN Transients', NULL),
(1016, 'tcs_cat_tns','Transient Name Server', 'https://wis-tns.weizmann.ac.il/');
