from __future__ import annotations

from dataclasses import dataclass

from database import Property, db
from sqlalchemy.sql import func


@dataclass
class Request(db.Model):

    __tablename__ = "request"  # Base.metadata.tables["af.request"]

    uuid = db.Column(db.String)
    category = db.Column(db.String)
    type = db.Column(db.String)
    design = db.Column(db.String)
    requestor_id = db.Column(db.String)
    institute = db.Column(db.String)
    crop = db.Column(db.String)
    program = db.Column(db.String)
    method_id = db.Column(db.Integer)
    engine = db.Column(db.String)
    msg = db.Column(db.String)
    status = db.Column(db.String)

    # TODO add the other columns here
    tasks = db.relationship("Task", backref="request", foreign_keys="Task.request_id")

    analyses = db.relationship("Analysis", back_populates="request")


@dataclass
class Job(db.Model):

    __tablename__ = "job"

    name = db.Column(db.String)
    time_start = db.Column(db.String)
    time_end = db.Column(db.String)
    output_path = db.Column(db.String)
    status = db.Column(db.String)
    status_message = db.Column(db.String)
