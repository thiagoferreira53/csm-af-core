from __future__ import annotations

from dataclasses import dataclass

from database import db
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
    model = db.Column(db.String) 
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    startdate = db.Column(db.String)
    enddate = db.Column(db.String)
    irrtype = db.Column(db.String)
    msg = db.Column(db.String)
    status = db.Column(db.String)

    engine = db.Column(db.String)


    # TODO add the other columns here
    tasks = db.relationship("Task_Simulation", backref="request_simulation", foreign_keys="Task_Simulation.request_id")

    simulation_req = db.relationship("Simulation_Data", back_populates="simulation_req")


@dataclass
class Simulation_Data(db.Model):

    __tablename__ = "simulation_data"

    name = db.Column(db.String)
    description = db.Column(db.String)
    request_id = db.Column(db.Integer, db.ForeignKey(Request_Simulation.id))
    status = db.Column(db.String)
    model = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    startdate = db.Column(db.String)
    enddate = db.Column(db.String)
    irrtype = db.Column(db.String)

    #analysis_request_data = db.Column(db.JSON)
    #additional_info = db.Column(db.JSON)

    simulation_req = db.relationship(Request_Simulation, back_populates="simulation_req")

    jobs = db.relationship("Job_Simulation", back_populates="simulation_req")


@dataclass
class Job_Simulation(db.Model):

    __tablename__ = "job_simulation"

    name = db.Column(db.String)
    time_start = db.Column(db.String)
    time_end = db.Column(db.String)
    output_path = db.Column(db.String)
    status = db.Column(db.String)
    status_message = db.Column(db.String)

    simulation_id = db.Column(db.Integer, db.ForeignKey(Simulation_Data.id))

    simulation_req = db.relationship(Simulation_Data, back_populates="jobs")