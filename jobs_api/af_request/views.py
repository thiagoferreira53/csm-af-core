from http import HTTPStatus
from typing import List, Optional

import config
import pydantic
from af_request import api_models, service
from common.api_models import Status
from common.responses import json_response
from common.validators import validate_api_request
from flask import jsonify, make_response, request, send_from_directory
from flask.blueprints import Blueprint
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

af_requests_bp = Blueprint("af_requests", __name__, url_prefix="/v1/csm/requests")


@af_requests_bp.route("", methods=["POST"])
@validate_api_request(body_model=api_models.AnalysisRequestParameters)
def post():
    """Create request object based on body params"""

    request_data = api_models.AnalysisRequestParameters(**request.json)

    submitted_analysis_request = service.submit(request_data)

    submitted_request_dto = _map_analysis(submitted_analysis_request)

    return json_response(submitted_request_dto, HTTPStatus.CREATED)


@af_requests_bp.route("", methods=["GET"])
@validate_api_request(query_model=api_models.AnalysisRequestListQueryParameters)
def list():
    """Create request object based on body params"""

    query_params = api_models.AnalysisRequestListQueryParameters(**request.args)

    analyses = service.query(query_params)

    # DTOs for api response
    analysis_request_dtos = []

    for analysis in analyses:
        analysis_request_dtos.append(_map_analysis(analysis))

    response = api_models.AnalysisRequestListResponse(
        metadata=api_models.create_metadata(query_params.page, query_params.pageSize),
        result=api_models.AnalysisRequestListResponseResult(data=analysis_request_dtos),
    )

    return json_response(response, HTTPStatus.OK)




def _map_analysis(analysis):
    """Maps the db result to the Result model."""

    req = analysis.request
    req_dto = api_models.AnalysisRequest(
        requestId=req.uuid,
        crop=req.crop,
        institute=req.institute,
        analysisType=req.type,
        status=req.status,
        createdOn=req.creation_timestamp,
        modifiedOn=req.modification_timestamp,
        requestorId=req.requestor_id,
        statusMessage=req.msg,
    )

    if req.analyses is not None and len(req.analyses) == 1:
        req_dto.analysisObjectiveProperty = _map_property(analysis.analysis_objective)
        req_dto.analysisConfigProperty = _map_property(analysis.model)
        req_dto.expLocAnalysisPatternProperty = _map_property(analysis.exp_loc_pattern)
        req_dto.configFormulaProperty = _map_property(analysis.formula)
        req_dto.configResidualProperty = _map_property(analysis.residual)

    if analysis.analysis_request_data is not None:
        req_dto.experiments = pydantic.parse_obj_as(
            List[api_models.Experiment], analysis.analysis_request_data.get("experiments", [])
        )
        req_dto.traits = pydantic.parse_obj_as(List[api_models.Trait], analysis.analysis_request_data.get("traits", []))

    if req.status == Status.DONE:
        req_dto.resultDownloadRelativeUrl = config.get_result_download_url(req.uuid)

    req_dto.jobs = []
    for job in analysis.jobs:
        req_dto.jobs.append(
            api_models.Job(
                jobId=job.id,
                jobName=job.name,
                status=job.status,
                statusMessage=job.status_message,
                startTime=job.time_start,
                endTime=job.time_end,
            )
        )

    return req_dto


def _map_property(_property):

    if _property is None:
        return None

    property_dto = api_models.Property(
        propertyId=_property.id,
        propertyCode=_property.code,
        propertyName=_property.name,
        label=_property.label,
        statement=_property.statement,
        type=_property.type,
        createdOn=_property.creation_timestamp,
        modifiedOn=_property.modification_timestamp,
    )

    return property_dto
