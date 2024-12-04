-- drop and create database for use in testing 
DROP DATABASE IF EXISTS `atlas_test`;
CREATE DATABASE `atlas_test`;

-- -- create user and grant rights
-- GRANT ALL ON atlas_test.* TO 'atlas'@'%';