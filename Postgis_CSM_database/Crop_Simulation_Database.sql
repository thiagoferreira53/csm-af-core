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

