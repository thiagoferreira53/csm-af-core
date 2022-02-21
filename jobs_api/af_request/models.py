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
class Analysis(db.Model):

    __tablename__ = "analysis"

    name = db.Column(db.String)
    description = db.Column(db.String)
    request_id = db.Column(db.Integer, db.ForeignKey(Request.id))
    status = db.Column(db.String)

    prediction_id = db.Column(db.Integer, db.ForeignKey(Property.id))
    model_id = db.Column(db.Integer, db.ForeignKey(Property.id))
    formula_id = db.Column(db.Integer, db.ForeignKey(Property.id))
    residual_id = db.Column(db.Integer, db.ForeignKey(Property.id))
    trait_analysis_pattern_id = db.Column(db.Integer, db.ForeignKey(Property.id))
    exp_loc_pattern_id = db.Column(db.Integer, db.ForeignKey(Property.id))
    analysis_objective_id = db.Column(db.Integer, db.ForeignKey(Property.id))

    analysis_request_data = db.Column(db.JSON)
    additional_info = db.Column(db.JSON)

    request = db.relationship(Request, back_populates="analyses")

    jobs = db.relationship("Job", back_populates="analysis")

    # map for all relationships to Property
    prediction = db.relationship(Property, foreign_keys=[prediction_id])
    model = db.relationship(Property, foreign_keys=[model_id])
    formula = db.relationship(Property, foreign_keys=[formula_id])
    residual = db.relationship(Property, foreign_keys=[residual_id])
    trait_analysis_pattern = db.relationship(Property, foreign_keys=[trait_analysis_pattern_id])
    exp_loc_pattern = db.relationship(Property, foreign_keys=[exp_loc_pattern_id])
    analysis_objective = db.relationship(Property, foreign_keys=[analysis_objective_id])


@dataclass
class Job(db.Model):

    __tablename__ = "job"

    name = db.Column(db.String)
    time_start = db.Column(db.String)
    time_end = db.Column(db.String)
    output_path = db.Column(db.String)
    status = db.Column(db.String)
    status_message = db.Column(db.String)

    analysis_id = db.Column(db.Integer, db.ForeignKey(Analysis.id))

    analysis = db.relationship(Analysis, back_populates="jobs")
