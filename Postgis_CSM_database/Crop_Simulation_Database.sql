--
-- PostGIS database
--

CREATE EXTENSION postgis;

CREATE TABLE Historical_Weather_RAIN
(
    RID BIGSERIAL NOT NULL,
    DATE DATE PRIMARY KEY,
    RAST RASTER,
    FILENAME TEXT,
    VARIABLE CHARACTER VARYING(10)
);

CREATE TABLE Historical_Weather_SRAD
(
    RID BIGSERIAL NOT NULL,
    DATE DATE PRIMARY KEY,
    RAST RASTER,
    FILENAME TEXT,
    VARIABLE CHARACTER VARYING(10)
);

CREATE TABLE Historical_Weather_TMIN
(
    RID BIGSERIAL NOT NULL,
    DATE DATE PRIMARY KEY,
    RAST RASTER,
    FILENAME TEXT,
    VARIABLE CHARACTER VARYING(10)
);

CREATE TABLE Historical_Weather_TMAX
(
    RID BIGSERIAL NOT NULL,
    DATE DATE PRIMARY KEY,
    RAST RASTER,
    FILENAME TEXT,
    VARIABLE CHARACTER VARYING(10)
);

CREATE TABLE soil
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE carbon
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE soil_water
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE winter_wheat
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE spring_wheat
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE n_irrigated
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE n_rainfed
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE init_res_mass
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE init_root_mass
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE soil_nitrogen
(
    RID BIGSERIAL NOT NULL,
    RAST RASTER,
    FILENAME TEXT
);

CREATE TABLE mega_env
(
    RID BIGSERIAL NOT NULL,
    NAME TEXT,
    RAST RASTER,
    FILENAME TEXT
);

/* TRIGGERS */

create or replace function raster_data_BI()returns trigger as $$
declare 
  v_date text;
Begin
  new.variable=split_part(new.filename,'_',1);
  v_date=split_part(new.filename,'_',2);
  v_date=substring(v_date,1,4) || '-' || substring(v_date,5,2) || '-' || substring(v_date,7,2); 
  new.date= cast(v_date as date); 
  return new;
end;
$$ language 'plpgsql';

create or replace function raster_data_ME()returns trigger as $$
declare 
  v_name text;
Begin
  v_name= split_part(new.filename,'_ME_',2);
  v_name = split_part(v_name,'.',1);
  new.name= cast(v_name as text); 
  return new;
end;
$$ language 'plpgsql';


create trigger raster_data_BI
    before insert
    on Historical_Weather_RAIN
    for each row
    execute procedure raster_data_BI();

create trigger raster_data_BI
    before insert
    on Historical_Weather_SRAD
    for each row
    execute procedure raster_data_BI();

create trigger raster_data_BI
    before insert
    on Historical_Weather_TMIN
    for each row
    execute procedure raster_data_BI();

create trigger raster_data_BI
    before insert
    on Historical_Weather_TMAX
    for each row
    execute procedure raster_data_BI();

create trigger raster_data_ME
    before insert
    on mega_env
    for each row
    execute procedure raster_data_ME();

-- 
-- request manager tables
--


DROP TABLE IF EXISTS request_simulation CASCADE;
DROP TABLE IF EXISTS task_simulation CASCADE;
DROP TABLE IF EXISTS job_simulation CASCADE;
DROP TABLE IF EXISTS simulation_data CASCADE;

DROP SEQUENCE IF EXISTS request_id_seq;
DROP SEQUENCE IF EXISTS task_id_seq;
DROP SEQUENCE IF EXISTS job_id_seq;
DROP SEQUENCE IF EXISTS simulation_data_id_seq;


CREATE TABLE request_simulation
(
	uuid TEXT NULL,
	category TEXT NULL,
	type TEXT NULL,
	requestor_id TEXT NULL,
	institute TEXT NULL,
	crop TEXT NULL,
    model TEXT NULL, 
    latitude TEXT NULL,
    longitude TEXT NULL,
    startdate TEXT NULL,
    enddate TEXT NULL,
    irrtype TEXT NULL,
    status TEXT NULL,
    msg TEXT NULL,
	creation_timestamp timestamp without time zone NULL,
	modification_timestamp timestamp without time zone NULL,
	creator_id TEXT NULL, --?
	modifier_id TEXT NULL, --?
	is_void boolean NULL, --?
    id integer NOT NULL   DEFAULT NEXTVAL(('"request_id_seq"'::text)::regclass),
    engine TEXT NULL
);

CREATE SEQUENCE request_id_seq INCREMENT 1 START 1;

 CREATE TABLE task_simulation
(
	name TEXT NULL,
	time_start timestamp without time zone NULL,
	time_end timestamp without time zone NULL,
	status TEXT NULL,
	err_msg TEXT NULL,
	processor TEXT NULL,
	creation_timestamp timestamp without time zone NOT NULL   DEFAULT now(),	-- Timestamp when the record was added to the table
	modification_timestamp timestamp without time zone NULL,	-- Timestamp when the record was last modified
	creator_id TEXT NOT NULL,	-- ID of the user who added the record to the table
	modifier_id TEXT NULL,	-- ID of the user who last modified the record
	is_void boolean NOT NULL   DEFAULT false,	-- Indicator whether the record is deleted (true) or not (false)
	id integer NOT NULL   DEFAULT NEXTVAL(('"task_id_seq"'::text)::regclass),
    request_id integer NULL
);

CREATE SEQUENCE task_id_seq INCREMENT 1 START 1;


CREATE TABLE job_simulation
(
	name TEXT NULL,
	time_start TEXT NULL,
	time_end TEXT NULL,
	output_path TEXT NULL,
	status TEXT NULL,
	status_message TEXT NULL,
	size TEXT NULL,
	creation_timestamp timestamp without time zone NULL,
	modification_timestamp timestamp without time zone NULL,
	creator_id TEXT NULL,
	modifier_id TEXT NULL,
	is_void boolean NULL,
	id integer NOT NULL   DEFAULT NEXTVAL(('"job_id_seq"'::text)::regclass),
    simulation_id integer NULL
);

CREATE SEQUENCE job_id_seq INCREMENT 1 START 1;

CREATE TABLE simulation_data
(
	name TEXT NULL,
	description TEXT NULL,
	status TEXT NULL,
	creation_timestamp timestamp without time zone NULL,
	modification_timestamp timestamp without time zone NULL,
	creator_id TEXT NULL,
	modifier_id TEXT NULL,
    model TEXT NULL, 
    latitude TEXT NULL,
    longitude TEXT NULL,
    startdate TEXT NULL,
    enddate TEXT NULL,
    irrtype TEXT NULL,
	is_void boolean NULL,
	id integer NOT NULL   DEFAULT NEXTVAL(('"simulation_data_id_seq"'::text)::regclass),
	request_id integer NULL
);

CREATE SEQUENCE simulation_data_id_seq INCREMENT 1 START 1;

ALTER TABLE task_simulation ADD CONSTRAINT "PK_task"
    PRIMARY KEY (id);

ALTER TABLE request_simulation ADD CONSTRAINT "PK_request"
	PRIMARY KEY (id);

ALTER TABLE job_simulation ADD CONSTRAINT "PK_job"
	PRIMARY KEY (id);

ALTER TABLE simulation_data ADD CONSTRAINT "PK_simulation_data"
	PRIMARY KEY (id);

ALTER TABLE task_simulation ADD CONSTRAINT "FK_task_request"
	FOREIGN KEY (request_id) REFERENCES request_simulation (id) ON DELETE No Action ON UPDATE No Action;

ALTER TABLE simulation_data ADD CONSTRAINT "FK_simulation_request"
	FOREIGN KEY (request_id) REFERENCES request_simulation (id) ON DELETE No Action ON UPDATE No Action;

ALTER TABLE job_simulation
 ALTER COLUMN creation_timestamp SET DEFAULT now();

ALTER TABLE job_simulation
 ALTER COLUMN is_void SET DEFAULT false;

ALTER TABLE simulation_data
 ALTER COLUMN creation_timestamp SET DEFAULT now();

ALTER TABLE simulation_data
 ALTER COLUMN is_void SET DEFAULT false;


--test

--INSERT INTO request_simulation(id, uuid, category, type, requestor_id, institute, crop, status, creation_timestamp, modification_timestamp, creator_id, modifier_id, is_void) VALUES
--(1, 'c1444c0d-d698-4ec6-9d18-02d96fb358c3', 1, 'Trial Design', 1, 'CIMMYT', 'wheat', 'new', null, null, '0', '0', false);


--INSERT INTO task_simulation(id, name, time_start,time_end,status,err_msg, processor, creation_timestamp, modification_timestamp, creator_id, modifier_id, is_void, request_id) VALUES
--(1,'a',null, null, 'new', 'abc', '1', now(), null, '1', '1', false, (select id from request_simulation where id = 1));
