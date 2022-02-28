import json
import uuid as uuidlib
from datetime import datetime

import celery_util
import pydantic
from af_request import api_models
from af_request import models as db_models
from database import db



def submit(request_params):
    """Submits analysis request to pipeline."""

    analysis_uuid = str(uuidlib.uuid4())

    req = db_models.Request(
        uuid=analysis_uuid,
        institute=request_params.institute,
        crop=request_params.crop,
        type=request_params.analysisType,
        requestor_id=request_params.requestorId,
        status="PENDING",
    )