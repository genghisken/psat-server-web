alter table tcs_gravity_event_annotations
add column `days_since_event` float
after `map_name`;

show warnings;

alter table tcs_gravity_event_annotations
add column `probability` float
after `days_since_event`;

show warnings;
