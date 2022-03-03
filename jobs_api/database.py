import datetime
from dataclasses import dataclass

import sqlalchemy as sa
from flask_sqlalchemy import Model, SessionBase, SignallingSession, SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func


# Base Model
class BaseModel(Model):

    __table_args__ = {"schema": "public"}

    id = sa.Column(sa.Integer, primary_key=True)
    creation_timestamp = sa.Column(sa.DateTime, server_default=func.now())
    modification_timestamp = sa.Column(sa.DateTime)
    creator_id = sa.Column(sa.String)
    modifier_id = sa.Column(sa.String)
    is_void = sa.Column(sa.Boolean, default=False)
    tenant_id = sa.Column(sa.Integer)


# database instance
db = SQLAlchemy(model_class=BaseModel)


@dataclass
class Task_Simulation(db.Model):
    id: int
    name: str
    time_start: datetime.datetime
    time_end: datetime.datetime
    status: str
    err_msg: str
    processor: str
    request_id: int

    __tablename__ = "task_simulation"

    name = db.Column(db.String)
    time_start = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)
    status = db.Column(db.String)
    err_msg = db.Column(db.String)
    processor = db.Column(db.String)
    request_id = db.Column(db.Integer, db.ForeignKey("public.request_simulation.id"))
    status = sa.Column(sa.String) #?

