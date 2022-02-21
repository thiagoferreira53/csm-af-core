import os
import datetime

from af_task_orchestrator.af.pipeline.db.core import Base
from geoalchemy2 import Raster
from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


from sqlalchemy import Column, Integer, String, Date

# workaround to get pytest to work with sqlite
if os.getenv("env") == "testing":
    pass
else:
    pass


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

class mega_environments(Base):
    __tablename__ = 'mega_env'
    rid = Column(Integer, primary_key=True)
    name = Column(String)
    rast = Column(Raster)
    filename = Column(String)



##FROM EBS

class BaseMixin(object):

    __table_args__ = {"schema": "af-core"}

    id = Column(Integer, primary_key=True)

    creation_timestamp = Column(DateTime, default=datetime.datetime.now())
    modification_timestamp = Column(DateTime, default=datetime.datetime.now())
    creator_id = Column(String)
    modifier_id = Column(String)
    is_void = Column(Boolean, default=False)




class Request(BaseMixin, Base):

    __tablename__ = "request"  # Base.metadata.tables["af-core.request"]

    uuid = Column(String)
    category = Column(String)
    type = Column(String)
    design = Column(String)
    requestor_id = Column(String)
    institute = Column(String)
    crop = Column(String)
    program = Column(String)
    tenant_id = Column(Integer)
    method_id = Column(Integer)

    engine = Column(String)

    status = Column(String)
    msg = Column(String)

    analyses = relationship("Analysis", back_populates="request")

    # TODO add the other columns here
    tasks = relationship("Task", backref="request")


class Task(BaseMixin, Base):

    __tablename__ = "task"

    name = Column(String)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    status = Column(String)
    err_msg = Column(String)
    processor = Column(String)
    tenant_id = Column(Integer, nullable=False)
    request_id = Column(Integer, ForeignKey("af-core.request.id"))
    parent_id = Column(Integer)

class Analysis(BaseMixin, Base):

    __tablename__ = "analysis"

    name = Column(String)
    description = Column(String)
    request_id = Column(Integer, ForeignKey(Request.id))
    prediction_id = Column(Integer)
    status = Column(String)
    tenant_id = Column(Integer)
    model_id = Column(Integer)

    request = relationship(Request, back_populates="analyses")

    jobs = relationship("Job", back_populates="analysis")


class Job(BaseMixin, Base):

    __tablename__ = "job"

    analysis_id = Column(Integer, ForeignKey(Analysis.id))
    name = Column(String)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    output_path = Column(String)
    status = Column(String)
    status_message = Column(String)
    tenant_id = Column(Integer)

    analysis = relationship(Analysis, back_populates="jobs")