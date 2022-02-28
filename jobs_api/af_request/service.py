import json
import uuid as uuidlib
from datetime import datetime

import celery_util
import pydantic
from af_request import api_models
from af_request import models as db_models
from database import db


class RequestData(pydantic.BaseModel):
    experiments: list[api_models.Experiment] = None
    traits: list[api_models.Trait] = None


