-- GRANTS script.  Must be run as the ROOT database user

-- KWS User -- Read-Only access and file-write permissions (for reports)
drop user 'kws'@'localhost';
create user 'kws'@'localhost';
grant select on *.* to 'kws'@'localhost';
grant file on *.* to 'kws'@'localhost';
grant execute on *.* to 'kws'@'localhost';
drop user 'kws'@'%';
create user 'kws'@'%';
grant select on *.* to 'kws'@'%';
grant file on *.* to 'kws'@'%';
grant execute on *.* to 'kws'@'%';

-- DRY User -- Read-Only access and file-write permissions (for reports)
drop user 'dry'@'localhost';
create user 'dry'@'localhost';
grant select on *.* to 'dry'@'localhost';
grant file on *.* to 'dry'@'localhost';
grant execute on *.* to 'dry'@'localhost';
drop user 'dry'@'%';
create user 'dry'@'%';
grant select on *.* to 'dry'@'%';
grant file on *.* to 'dry'@'%';
grant execute on *.* to 'dry'@'%';

-- DEW User -- Read-Only access and file-write permissions (for reports)
drop user 'dew'@'localhost';
create user 'dew'@'localhost';
grant select on *.* to 'dew'@'localhost';
grant file on *.* to 'dew'@'localhost';
grant execute on *.* to 'dew'@'localhost';
drop user 'dew'@'%';
create user 'dew'@'%';
grant select on *.* to 'dew'@'%';
grant file on *.* to 'dew'@'%';
grant execute on *.* to 'dew'@'%';

-- SNE User -- Read-Only access and file-write permissions (for reports)
drop user 'sne'@'localhost';
create user 'sne'@'localhost';
grant select on *.* to 'sne'@'localhost';
grant file on *.* to 'sne'@'localhost';
grant execute on *.* to 'sne'@'localhost';
drop user 'sne'@'%';
create user 'sne'@'%';
grant select on *.* to 'sne'@'%';
grant file on *.* to 'sne'@'%';
grant execute on *.* to 'sne'@'%';

-- ORMB User -- Read-Only access and file-write permissions (for reports)
drop user 'ormb'@'localhost';
create user 'ormb'@'localhost';
grant select on *.* to 'ormb'@'localhost';
grant file on *.* to 'ormb'@'localhost';
grant execute on *.* to 'ormb'@'localhost';
drop user 'ormb'@'%';
create user 'ormb'@'%';
grant select on *.* to 'ormb'@'%';
grant file on *.* to 'ormb'@'%';
grant execute on *.* to 'ormb'@'%';

-- MDF User -- Read-Only access and file-write permissions (for reports)
drop user 'mdf'@'localhost';
create user 'mdf'@'localhost';
grant select on *.* to 'mdf'@'localhost';
grant file on *.* to 'mdf'@'localhost';
grant execute on *.* to 'mdf'@'localhost';
drop user 'mdf'@'%';
create user 'mdf'@'%';
grant select on *.* to 'mdf'@'%';
grant file on *.* to 'mdf'@'%';
grant execute on *.* to 'mdf'@'%';

-- MEMC User -- Read-Only access and file-write permissions (for reports)
drop user 'memc'@'localhost';
create user 'memc'@'localhost';
grant select on *.* to 'memc'@'localhost';
grant file on *.* to 'memc'@'localhost';
grant execute on *.* to 'memc'@'localhost';
drop user 'memc'@'%';
create user 'memc'@'%';
grant select on *.* to 'memc'@'%';
grant file on *.* to 'memc'@'%';
grant execute on *.* to 'memc'@'%';

-- MDF User -- Read-Only access and file-write permissions (for reports)
drop user 'mdf'@'localhost';
create user 'mdf'@'localhost';
grant select on *.* to 'mdf'@'localhost';
grant file on *.* to 'mdf'@'localhost';
grant execute on *.* to 'mdf'@'localhost';
drop user 'mdf'@'%';
create user 'mdf'@'%';
grant select on *.* to 'mdf'@'%';
grant file on *.* to 'mdf'@'%';
grant execute on *.* to 'mdf'@'%';

