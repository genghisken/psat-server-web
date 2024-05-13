alter table tcs_gravity_alerts
add column `interesting` tinyint(4)
after `map`;

show warnings;
