DROP DATABASE IF EXISTS devdb WITH (FORCE);
CREATE DATABASE devdb;
\connect devdb;
CREATE SCHEMA gringotts;

DROP DATABASE IF EXISTS testdb WITH (FORCE);
CREATE DATABASE testdb;
\connect testdb;
CREATE SCHEMA gringotts;
