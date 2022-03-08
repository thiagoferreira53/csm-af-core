from af_task_orchestrator.af.pipeline.db.models import Job_Simulation, weather_rain, weather_tmax, weather_tmin, weather_srad
from af_task_orchestrator.af.pipeline.db.models import mega_environments_wheat, soil, carbon, soil_water, \
    init_residue_mass, init_root_mass, soil_nitrogen, Request_Simulation
from af_task_orchestrator.af.pipeline.db.models import plating_date_winter_wheat, plating_date_spring_wheat, \
    nitrogen_app_irrigated, nitrogen_app_rainfed

from datetime import datetime
from geoalchemy2.elements import WKTElement

def coord_to_point(latitude: float, longitude: float):
    point_str = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'

    # WKTElement substitutes st_makepoint function from postgis
    point = WKTElement(point_str, srid=4326)
    return point

def get_daily_weather_info(dbsession, start_date: str, end_date: str, latitude: float, longitude: float):
    sdate = datetime.strptime(start_date, '%Y/%m/%d')
    edate = datetime.strptime(end_date, '%Y/%m/%d')

    wkt_element = coord_to_point(latitude,longitude)

    weather = (dbsession.query(weather_rain.date, weather_rain.rast.ST_Value(wkt_element),
                             weather_tmax.rast.ST_Value(wkt_element),
                      weather_tmin.rast.ST_Value(wkt_element), weather_srad.rast.ST_Value(wkt_element))
              .join(weather_tmax, weather_rain.date == weather_tmax.date)
              .join(weather_tmin, weather_tmax.date == weather_tmin.date)
              .join(weather_srad, weather_tmin.date == weather_srad.date)
              .filter(weather_rain.date >= sdate)
              .filter(weather_rain.date <= edate))
    return weather


def get_mega_env_id_wheat(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)

    mega_env_id = (dbsession.query(mega_environments_wheat.name)
                   .filter(mega_environments_wheat.rast.ST_Value(wkt_element) == 1)) #selects only the first value
    return mega_env_id


#return only the id. This id must be added to the end of "HN_GEN00" string
def get_soil_id(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(soil.rast.ST_Value(wkt_element)))
    return mega_env_id

def get_carbon_value(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(carbon.rast.ST_Value(wkt_element)))
    return mega_env_id

def get_soil_water_value(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(soil_water.rast.ST_Value(wkt_element)))
    return mega_env_id

def get_init_residue_mass_value(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(init_residue_mass.rast.ST_Value(wkt_element)))
    return mega_env_id

def get_init_root_mass_value(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(init_root_mass.rast.ST_Value(wkt_element)))
    return mega_env_id

def get_soil_nitrogen_value(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(soil_nitrogen.rast.ST_Value(wkt_element)))
    return mega_env_id

#returns the month of planting
def get_plating_date_winter_wheat(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(plating_date_winter_wheat.rast.ST_Value(wkt_element)))
    return mega_env_id

#returns the month of planting
def get_plating_date_spring_wheat(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(plating_date_spring_wheat.rast.ST_Value(wkt_element)))
    return mega_env_id

def get_nitrogen_app_irrigated_value(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(nitrogen_app_irrigated.rast.ST_Value(wkt_element)))
    return mega_env_id

def get_nitrogen_app_rainfed_value(dbsession, latitude: float, longitude: float):
    wkt_element = coord_to_point(latitude,longitude)
    mega_env_id = (dbsession.query(nitrogen_app_rainfed.rast.ST_Value(wkt_element)))
    return mega_env_id


#EBS

def add(db_session, _object):
    db_session.add(_object)
    db_session.commit()
    return _object


def create_job_simulation(db_session, job_id: int, job_name: str, status: str, status_message: str) -> Job_Simulation:

    job_start_time = datetime.utcnow()
    job = Job_Simulation(
        simulation_id=job_id,
        name=job_name,
        time_start=job_start_time,
        creation_timestamp=job_start_time,
        status=status,
        status_message=status_message,
    )

    job = add(db_session, job)

    return job

def update_job(db_session, job: Job_Simulation, status: str, status_message: str):

    job.status = status
    job.status_message = status_message
    job.time_end = datetime.utcnow()
    job.modification_timestamp = datetime.utcnow()

    return job

def get_simulation_by_request_id(db_session, request_id):
    return db_session.query(Request_Simulation).filter(Request_Simulation.uuid == request_id).first()