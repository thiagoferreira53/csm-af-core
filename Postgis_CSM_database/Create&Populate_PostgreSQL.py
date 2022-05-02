#!/usr/local/bin/python3

import psycopg2
import os

cfg={}
def readConfig():
    confPath = os.getcwd() +"/db_info.conf"

    simbaConf = open(confPath, 'r')

    line = simbaConf.readline()

    while line:
        if not line.startswith("#"):
            line = line.strip()
            key, value = line.split("=")
            cfg[key] = value
        line = simbaConf.readline()

    simbaConf.close()

readConfig()

workDir =cfg['rtd']
user = cfg['dbu']
dbName = cfg['dbnw']
dbPort=cfg['dpt']
pwd = cfg['dbp']


# IMPORTANT: Only execute this script after generating the tiff files using the csv_to_tiff.R script


dbVariables = ["rain", "srad", "tmin", "tmax"]

conn = psycopg2.connect("dbname=" +dbName + " user=" + user + " password=" + pwd +" port=" + dbPort)
print(conn)
cursor = conn.cursor()

#cursor.execute("CREATE EXTENSION postgis;")
#cursor.execute("CREATE EXTENSION postgis_raster;")

triggerFunction = "create or replace function raster_data_BI()returns trigger as $$\ndeclare\n  v_date text;\n  v_version text;\n" \
    "Begin\n  new.variable=split_part(new.filename,'_',1);\n  v_date=split_part(new.filename,'_',2);" \
    "\n  v_date=substring(v_date,1,4) || '-' || substring(v_date,5,2) || '-' || substring(v_date,7,2);\n  new.date= cast(v_date as date);" \
    "\n  return new;\nend;\n$$ language 'plpgsql';"

cursor.execute(triggerFunction)

for i in dbVariables:

    sqlCreateTable = "CREATE TABLE IF NOT EXISTS historical_weather_" + i + "\n(\n    RID BIGSERIAL NOT NULL,\n    DATE DATE PRIMARY KEY," \
        "\n    RAST RASTER,\n    FILENAME TEXT,\n    VARIABLE CHARACTER VARYING(10)\n);"
    print(sqlCreateTable)
    cursor.execute(sqlCreateTable)

    triggerDB = "create or replace trigger raster_data_BI\n    before insert\n    on historical_weather_" + i + "\n    for each row" \
        "\n    execute procedure raster_data_BI();"

    cursor.execute(triggerDB)

    conn.commit()

    os.system("raster2pgsql -a -s 4326 -I -M -F -C " + workDir + "/weather_data/tiff_outputs/"+ i.upper() +"/*.tif public.historical_weather_"+i+" | "
                "PGPASSWORD="+ pwd +" psql -U " + user + " -d weather_data -h localhost -p 5432")


#MEGA ENVIRONMENTS

GlobalData = ["soil", "carbon", "soil_water", "winter_wheat", "spring_wheat","n_irrigated",\
              "n_rainfed","init_res_mass","init_root_mass","soil_nitrogen"]

triggerFunction = "create or replace function raster_data_GD()returns trigger as $$"\
"\ndeclare"\
"\n  v_id integer;"\
"\nBegin"\
"\n  v_id = 1;"\
"\n  new.id = cast(v_id as integer);"\
"\n  return new;"\
"\nend;"\
"\n$$ language 'plpgsql';"

cursor.execute(triggerFunction)


for j in GlobalData:
    sqlCreateTable = "CREATE TABLE IF NOT EXISTS " + j + "\n(\n    ID INT PRIMARY KEY,\n    RID BIGSERIAL NOT NULL," \
        "\n    RAST RASTER,\n    FILENAME TEXT\n);"
    print(sqlCreateTable)
    cursor.execute(sqlCreateTable)
    conn.commit()

    triggerGD = "create or replace trigger raster_data_GD\n    before insert\n    on " + j + "\n    for each row" \
        "\n    execute procedure raster_data_GD();"

    cursor.execute(triggerGD)
    conn.commit()

    os.system("raster2pgsql -a -s 4326 -I -M -F -C " + workDir + "/global_wheat_data/"+ j +".asc public."+j+" | "
                "PGPASSWORD="+ pwd + " psql -U " + user + " -d weather_data -h localhost -p 5432")
    print("raster2pgsql -a -s 4326 -I -M -F -C " + workDir + "/global_wheat_data/"+ j +".asc public."+j+" | "
                "PGPASSWORD="+ pwd + " psql -U " + user + " -d weather_data -h localhost -p 5432")

triggerFunctionME = "create or replace function raster_data_ME()returns trigger as $$"\
"\ndeclare"\
"\n  v_name text;"\
"\nBegin"\
"\n  v_name= split_part(new.filename,'_ME_',2);"\
"\n  v_name = split_part(v_name,'.',1);"\
"\n  new.name= cast(v_name as text);"\
"\n  return new;"\
"\nend;"\
"\n$$ language 'plpgsql';"

cursor.execute(triggerFunctionME)

sqlCreateTable = "\nCREATE TABLE IF NOT EXISTS mega_env"\
"\n("\
"\n    RID BIGSERIAL NOT NULL,"\
"\n    NAME TEXT PRIMARY KEY,"\
"\n    RAST RASTER,"\
"\n    FILENAME TEXT"\
"\n);"

print(sqlCreateTable)
cursor.execute(sqlCreateTable)
conn.commit()

triggerDB = "create or replace trigger raster_data_ME"\
"\n    before insert" \
"\n    on mega_env"\
"\n    for each row"\
"\n    execute procedure raster_data_ME();"
cursor.execute(triggerDB)
conn.commit()

os.system("raster2pgsql -a -s 4326 -I -M -F -C " + workDir + "/global_wheat_data/ME/*.asc public.mega_env | "
          "PGPASSWORD="+ pwd +" psql -U " + user + " -d weather_data -h localhost -p 5432")

print("raster2pgsql -a -s 4326 -I -M -F -C " + workDir + "/global_wheat_data/ME/*.asc public.mega_env | "
          "PGPASSWORD="+ pwd +" psql -U " + user + " -d weather_data -h localhost -p 5432")
#Weather_file function

func_weather_file = "CREATE OR REPLACE FUNCTION weather_file(lat numeric, long numeric, iniDate date, endDate date)"\
"\nRETURNS TABLE (date date,"\
"\n              rain double precision,"\
"\n              tmax double precision,"\
"\n              tmin double precision,"\
"\n              srad double precision) AS $$"\
"\nBEGIN"\
"\n    RETURN QUERY"\
"\n    SELECT rainwd.date::date, st_value(rainwd.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(tmaxwd.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(tminwd.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(sradwd.rast, st_setsrid(st_makepoint(long,lat), 4326))"\
"\n    FROM historical_weather_rain as rainwd"\
"\n    inner join historical_weather_tmax as tmaxwd on"\
"\n    rainwd.date = tmaxwd.date"\
"\n    inner join historical_weather_tmin as tminwd on"\
"\n    rainwd.date = tminwd.date"\
"\n    inner join historical_weather_srad as sradwd on"\
"\n    rainwd.date = sradwd.date"\
"\n    where rainwd.date >= iniDate"\
"\n    AND rainwd.date <= endDate;"\
"\nEND"\
"\n$$ LANGUAGE plpgsql;"

print(func_weather_file)
cursor.execute(func_weather_file)
conn.commit()


func_global_data = "\nCREATE OR REPLACE FUNCTION global_data(lat numeric, long numeric)"\
"\nRETURNS TABLE (soil double precision,"\
"\n              carbon double precision,"\
"\n              init_res_mass double precision,"\
"\n              init_root_mass double precision,"\
"\n              n_irrigated double precision,"\
"\n              n_rainfed double precision,"\
"\n              soil_nitrogen double precision,"\
"\n              soil_water double precision,"\
"\n              spring_wheat double precision,"\
"\n              winter_wheat double precision) AS $$"\
"\nBEGIN"\
"\n    RETURN QUERY"\
"\n    SELECT st_value(soil.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(carbon.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(initial_res_mass.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(initial_root_mass.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(n_irrigated.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(n_rainfed.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(soil_nitrogen.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(soil_water.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(spring_wheat.rast, st_setsrid(st_makepoint(long,lat), 4326)),"\
"\n    st_value(winter_wheat.rast, st_setsrid(st_makepoint(long,lat), 4326))"\
"\n    FROM soil"\
"\n    inner join carbon on"\
"\n    soil.id = carbon.id"\
"\n    inner join initial_res_mass on"\
"\n    soil.id = initial_res_mass.id"\
"\n    inner join initial_root_mass on"\
"\n    soil.id = initial_root_mass.id"\
"\n    inner join n_irrigated on"\
"\n    soil.id = n_irrigated.id"\
"\n    inner join n_rainfed on"\
"\n    soil.id = n_rainfed.id"\
"\n    inner join soil_nitrogen on"\
"\n    soil.id = soil_nitrogen.id"\
"\n    inner join soil_water on"\
"\n    soil.id = soil_water.id"\
"\n    inner join spring_wheat on"\
"\n    soil.id = spring_wheat.id"\
"\n    inner join winter_wheat on"\
"\n    soil.id = winter_wheat.id;"\
"\nEND"\
"\n$$ LANGUAGE plpgsql;"

cursor.execute(func_global_data)
conn.commit()

func_ME = "CREATE OR REPLACE FUNCTION data_mega_env(lat numeric, long numeric)"\
"\nRETURNS TABLE (ME_name text) AS $$"\
"\nBEGIN"\
"\n    RETURN QUERY"\
"\n    SELECT name"\
"\n    FROM mega_env"\
"\n    WHERE st_value(mega_env.rast, st_setsrid(st_makepoint(long,lat), 4326)) =1;"\
"\nEND"\
"\n$$ LANGUAGE plpgsql;"

cursor.execute(func_ME)
conn.commit()
