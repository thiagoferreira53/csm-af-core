from __future__ import annotations

from dataclasses import dataclass

from database import Property, db
from sqlalchemy.sql import func


@dataclass
class Request_Simulation(db.Model):

    __tablename__ = "request_simulation"  # Base.metadata.tables["af.request"]

    uuid = db.Column(db.String)
    category = db.Column(db.String)
    type = db.Column(db.String)
    requestor_id = db.Column(db.String)
    institute = db.Column(db.String)
    crop = db.Column(db.String)
    msg = db.Column(db.String)
    status = db.Column(db.String)

    # TODO add the other columns here
    tasks = db.relationship("Task_Simulation", backref="request", foreign_keys="Task_Simulation.request_id")



@dataclass
class Job_Simulation(db.Model):

    __tablename__ = "job_simulation"

    job_id = db.Column(db.Integer)
    name = db.Column(db.String)
    time_start = db.Column(db.String)
    time_end = db.Column(db.String)
    output_path = db.Column(db.String)
    status = db.Column(db.String)
    status_message = db.Column(db.String)
