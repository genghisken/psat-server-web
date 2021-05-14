-- We need to be able to have root login from SPECIFIC remote machines.
-- DO NOT USE '%' for the root user host.  It just doesn't work.

grant all privileges on *.* to 'root'@'psfiles' identified by 'panstarrs1' with grant option;
