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
@validate_api_request(body_model=api_models.CropSimulationRequestParameters)
def post():
    """Create request object based on body params"""

    request_data = api_models.CropSimulationRequestParameters(**request.json)

    submitted_analysis_request = service.submit(request_data)

    submitted_request_dto = _map_analysis(submitted_analysis_request)

    return json_response(submitted_request_dto, HTTPStatus.CREATED)


def _map_analysis(analysis):
    """Maps the db result to the Result model."""

    req = analysis.simulation_req
    req_dto = api_models.CropSimulationRequest(
        requestId=req.uuid,
        requestorId=req.requestor_id,
        crop=req.crop,
        institute=req.institute,
        analysisType=req.type,
        model = analysis.model,
        latitude = analysis.latitude,
        longitude = analysis.longitude,
        startdate = analysis.startdate,
        enddate = analysis.enddate,
        irrtype = analysis.irrtype,
        status=req.status,
        statusMessage=req.msg,
        createdOn=req.creation_timestamp,
        modifiedOn=req.modification_timestamp,
    )

    return req_dto
