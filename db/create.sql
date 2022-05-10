SELECT 'CREATE DATABASE devdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'devdb')\gexec
\connect devdb;
CREATE SCHEMA gringotts;

SELECT 'CREATE DATABASE testdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'testdb')\gexec\connect testdb;
DROP SCHEMA IF EXISTS gringotts;
CREATE SCHEMA gringotts;
