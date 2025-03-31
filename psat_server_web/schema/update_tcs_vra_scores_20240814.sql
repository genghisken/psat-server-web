alter table tcs_vra_scores
add column `rank` float after `pfast`,
add column `rank_alt1` float after `rank`,
add column `rank_alt2` float after `rank_alt1`
;

