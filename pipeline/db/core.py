from pipeline import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class DBConfig:
    _engine = None

    @classmethod
    def get_engine(cls):
        if DBConfig._engine:
            return DBConfig._engine
        DBConfig._engine = create_engine(config.AFDB_URI, pool_pre_ping=True)
        return DBConfig._engine

    _SessionLocal = None

    @staticmethod
    def get_session():
        if DBConfig._SessionLocal:
            return DBConfig._SessionLocal
        DBConfig._SessionLocal = scoped_session(sessionmaker(DBConfig.get_engine()))
        print("Postgis Database Connection - success")
        return DBConfig._SessionLocal


Base = declarative_base()
