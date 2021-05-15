create or replace view psdb_web_v_2mass_psc_cat as select * from DATABASE.tcs_2mass_psc_cat;
create or replace view psdb_web_v_2mass_xsc_cat as select * from DATABASE.tcs_2mass_xsc_cat;
create or replace view psdb_web_v_guide_star_cat as select * from DATABASE.tcs_guide_star_cat;
create or replace view psdb_web_v_ned_cat as select * from DATABASE.tcs_ned_cat;
create or replace view psdb_web_v_sdss_galaxies_cat as select * from DATABASE.tcs_sdss_galaxies_cat;
create or replace view psdb_web_v_sdss_spect_galaxies_cat as select * from DATABASE.tcs_sdss_spect_galaxies_cat;
create or replace view psdb_web_v_sdss_stars_cat as select * from DATABASE.tcs_sdss_stars_cat;
create or replace view psdb_web_v_veron_cat as select * from DATABASE.tcs_veron_cat;
create or replace view psdb_web_v_cat_sdss_stars_galaxies as select * from DATABASE.tcs_cat_sdss_stars_galaxies;

-- New catalogues

create or replace view psdb_web_v_cat_milliquas as select * from DATABASE.tcs_cat_milliquas;
