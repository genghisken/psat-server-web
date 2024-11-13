-- create databases
CREATE DATABASE IF NOT EXISTS `atlas_test`;

-- create user and grant rights
GRANT ALL ON atlas_test.* TO 'atlas'@'%';
