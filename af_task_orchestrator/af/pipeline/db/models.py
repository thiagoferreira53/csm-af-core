import os
import datetime

from af_task_orchestrator.af.pipeline.db.core import Base
from geoalchemy2 import Raster
from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


from sqlalchemy import Column, Integer, String, Date

class weather_rain(Base):
    __tablename__ = "historical_weather_rain"

    rid = Column(Integer)
    date = Column(Date, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)
    variable = Column(String)

class weather_tmax(Base):
    __tablename__ = "historical_weather_tmax"

    rid = Column(Integer)
    date = Column(Date, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)
    variable = Column(String)

class weather_tmin(Base):
    __tablename__ = "historical_weather_tmin"

    rid = Column(Integer)
    date = Column(Date, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)
    variable = Column(String)

class weather_srad(Base):
    __tablename__ = "historical_weather_srad"

    rid = Column(Integer)
    date = Column(Date, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)
    variable = Column(String)

class soil(Base):
    __tablename__ = 'soil'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class carbon(Base):
    __tablename__ = 'carbon'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class soil_water(Base):
    __tablename__ = 'soil_water'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class plating_date_winter_wheat(Base):
    __tablename__ = 'winter_wheat' #maybe change this name
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class plating_date_spring_wheat(Base):
    __tablename__ = 'spring_wheat' #maybe change this name
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class nitrogen_app_irrigated(Base):
    __tablename__ = 'n_irrigated'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class nitrogen_app_rainfed(Base):
    __tablename__ = 'n_rainfed'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class init_residue_mass(Base):
    __tablename__ = 'init_res_mass'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class init_root_mass(Base):
    __tablename__ = 'init_root_mass'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class soil_nitrogen(Base):
    __tablename__ = 'soil_nitrogen'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String)

class mega_environments_wheat(Base):
    __tablename__ = 'mega_env' #?# must change the table name later on
    rid = Column(Integer, primary_key=True)
    name = Column(String)
    rast = Column(Raster)
    filename = Column(String)



##FROM EBS

class BaseMixin(object):

    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)

    creation_timestamp = Column(DateTime, default=datetime.datetime.now())
    modification_timestamp = Column(DateTime, default=datetime.datetime.now())
    creator_id = Column(String)
    modifier_id = Column(String)
    is_void = Column(Boolean, default=False)



class Request_Simulation(BaseMixin, Base):

    __tablename__ = "request_simulation"  # Base.metadata.tables["af-core.request"]

    uuid = Column(String)
    category = Column(String)
    type = Column(String)
    requestor_id = Column(String)
    institute = Column(String)
    crop = Column(String)
    status = Column(String)
    msg = Column(String)

    # TODO add the other columns here
    tasks = relationship("Task_Simulation", backref="request_simulation")
    


class Task_Simulation(BaseMixin, Base):

    __tablename__ = "task_simulation"

    name = Column(String)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    status = Column(String)
    err_msg = Column(String)
    processor = Column(String)
    request_id = Column(Integer, ForeignKey("public.request_simulation.id"))

class Job_Simulation(BaseMixin, Base):

    __tablename__ = "job_simulation"

    job_id = Column(Integer) #?# removed foreign keys from Analysis - Added job_id
    name = Column(String)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    output_path = Column(String)
    status = Column(String)
    status_message = Column(String)
