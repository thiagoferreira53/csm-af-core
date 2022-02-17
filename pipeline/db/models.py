import os
from pipeline.db.core import Base
from geoalchemy2 import Raster


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

