CREATE ROLE test LOGIN
  ENCRYPTED PASSWORD 'md505a671c66aefea124cc08b76ea6d30bb'
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;


CREATE DATABASE test
  WITH OWNER = test
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'Russian_Russia.1251'
       LC_CTYPE = 'Russian_Russia.1251'
       CONNECTION LIMIT = -1;
GRANT ALL ON DATABASE test TO test;
GRANT ALL ON DATABASE test TO public;

-- Table: nodes

-- DROP TABLE nodes;

CREATE TABLE nodes
(
  id integer NOT NULL,
  parent_id integer,
  label character varying(256),
  level integer,
  CONSTRAINT nodes_pkey PRIMARY KEY (id),
  CONSTRAINT nodes_parent_id_fkey FOREIGN KEY (parent_id)
      REFERENCES nodes (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE nodes
  OWNER TO test;

-- Index: levels_idx

-- DROP INDEX levels_idx;

CREATE INDEX levels_idx
  ON nodes
  USING btree
  (level);