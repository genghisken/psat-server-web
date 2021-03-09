-- GRANTS script.  Must be run as the ROOT database user

-- Web User -- Has Read/Write access to relevant Transient tables, but read-only access to others (e.g. catalogues)
drop user 'django'@'psfiles';
grant all on django.* to 'django'@'psfiles' identified by 'django';

-- Read-Only access for all the Transient Tables
grant select on panstarrs1.* to 'django'@'psfiles';

-- Limited access for Transient helper tables
grant select, insert, update on panstarrs1.tcs_images to 'django'@'psfiles';
grant select, insert, delete, update on panstarrs1.tcs_classification_history to 'django'@'psfiles';

-- Very limited access to Transient Objects
grant update(date_modified, object_classification, followup_priority, external_reference_id, tcs_images_id) on panstarrs1.tcs_transient_objects to 'django'@'psfiles';

