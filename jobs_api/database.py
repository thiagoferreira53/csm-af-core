import datetime
from dataclasses import dataclass

import sqlalchemy as sa
from flask_sqlalchemy import Model, SessionBase, SignallingSession, SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func


# Base Model
class BaseModel(Model):

    __table_args__ = {"schema": "af"}

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
class Task(db.Model):
    id: int
    name: str
    time_start: datetime.datetime
    time_end: datetime.datetime
    status: str
    err_msg: str
    processor: str
    request_id: int

    __tablename__ = "task"

    name = db.Column(db.String)
    time_start = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)
    status = db.Column(db.String)
    err_msg = db.Column(db.String)
    processor = db.Column(db.String)
    tenant_id = db.Column(db.Integer, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("af.request.id"))
    parent_id = db.Column(db.Integer)
    status = sa.Column(sa.String)


@dataclass
class Property(db.Model):

    code: str
    name: str
    label: str
    description: str
    type: str
    data_type: str
    creation_timestamp: datetime.datetime
    modification_timestamp: datetime.datetime
    creator_id: str
    modifier_id: str
    id: int
    statement: str
    is_void: bool

    __tablename__ = "property"
    __table_args__ = {"schema": "af"}

    code = db.Column(db.String)
    name = db.Column(db.String)
    label = db.Column(db.String)
    description = db.Column(db.String)
    type = db.Column(db.String)
    data_type = db.Column(db.String)
    tenant_id = db.Column(db.Integer)
    statement = db.Column(db.String)

    property_configs = db.relationship("PropertyConfig", backref="property", foreign_keys="PropertyConfig.property_id")


@dataclass
class PropertyConfig(db.Model):

    __tablename__ = "property_config"
    __table_args__ = {"schema": "af"}

    # TODO:  define columns and Foreign key here
    is_required = db.Column(db.Boolean, default=False)
    order_number = db.Column(db.Integer, default=1)
    tenant_id = db.Column(db.Integer)
    property_id = db.Column(db.Integer, db.ForeignKey("af.property.id"))
    config_property_id = db.Column(db.Integer)
    property_ui_id = db.Column(db.Integer, db.ForeignKey("af.property_ui.id"))
    is_layout_variable = db.Column(db.Boolean, default=False)

    # relationship def one to one?
    property_ui = db.relationship("PropertyUI", backref=db.backref("property_config", uselist=False))


@dataclass
class PropertyUI(db.Model):
    __tablename__ = "property_ui"
    __table_args__ = {"schema": "af"}

    is_visible = db.Column(db.Boolean, default=True)
    minimum = db.Column(db.Integer)
    maximum = db.Column(db.Integer)
    unit = db.Column(db.String)
    default = db.Column(db.String)
    is_disabled = db.Column(db.Boolean, default=False)
    is_multiple = db.Column(db.Boolean, default=False)
    is_catalogue = db.Column(db.Boolean, default=False)
    tenant_id = db.Column(db.Integer)
