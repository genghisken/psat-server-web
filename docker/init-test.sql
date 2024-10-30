-- create databases
CREATE DATABASE IF NOT EXISTS `test_atlas`;

-- create root user and grant rights
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin';
GRANT ALL ON *.* TO 'admin'@'localhost';
