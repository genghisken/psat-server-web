alter table tcs_gravity_event_annotations
add column `days_since_event` float
after `map_name`;

show warnings;

alter table tcs_gravity_event_annotations
add column `probability` float
after `days_since_event`;

show warnings;

alter table tcs_gravity_event_annotations
add column `map_iteration` varchar(100)
after `map_name`;

show warnings;

alter table tcs_gravity_event_annotations
add column `distance` float
after `probability`;

show warnings;

alter table tcs_gravity_event_annotations
add column `distance_sigma` float
after `distance`;

show warnings;

drop index `transient_gracedb` on tcs_gravity_event_annotations;
show warnings;

alter table tcs_gravity_event_annotations
add unique key `key_transient_gracedb_iteration` (transient_object_id, gravity_event_id, map_iteration);
show warnings;
