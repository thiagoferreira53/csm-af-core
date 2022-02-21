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


def submit(request_params: api_models.AnalysisRequestParameters):
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

    req_data = RequestData(**request_params.dict())

    additionalInfo = {"data_sources":
    [{'source' : request_params.dataSource, 'url' : request_params.dataSourceUrl, 'token' : request_params.dataSourceAccessToken}]}

    analysis = db_models.Analysis(
        request=req,
        name=analysis_uuid,
        creation_timestamp=datetime.utcnow(),
        status="IN-PROGRESS",
        analysis_objective_id=request_params.analysisObjectivePropertyId,
        formula_id=request_params.configFormulaPropertyId,
        residual_id=request_params.configResidualPropertyId,
        exp_loc_pattern_id=request_params.expLocAnalysisPatternPropertyId,
        model_id=request_params.analysisConfigPropertyId,
        analysis_request_data=req_data.dict(),
        additional_info=additionalInfo
    )
    with db.session.begin():
        db.session.add(analysis)

        celery_util.send_task(
            process_name="analyze",
            args=(
                req.uuid,
                json.loads(request_params.json()),
            ),
        )

    return analysis


def query(query_params: api_models.AnalysisRequestListQueryParameters) -> db_models.Analysis:

    query = db_models.Analysis.query.join(db_models.Request)

    # filter only analysis requests.
    # Requests submitted by other frameworks have non standardized status fields other than what
    # used by af.
    query = query.filter(db_models.Request.type == "ANALYZE")

    if query_params.requestorId:
        query = query.filter(db_models.Request.requestor_id == query_params.requestorId)

    if query_params.crop:
        query = query.filter(db_models.Request.crop == query_params.crop)

    if query_params.institute:
        query = query.filter(db_models.Request.institute == query_params.institute)

    if query_params.status:
        query = query.filter(db_models.Request.status == query_params.status)

    # Get latest requests first
    query = query.order_by(db_models.Request.creation_timestamp.desc())

    # AnalysisRequestListQueryParameters have default page and pageSize
    query = query.limit(query_params.pageSize).offset(query_params.page * query_params.pageSize)

    analysis_requests = query.all()

    return analysis_requests


def get_by_id(request_id: str):

    analysis_request = (
        db_models.Analysis.query.join(db_models.Request).filter(db_models.Request.uuid == request_id).one()
    )

    return analysis_request
