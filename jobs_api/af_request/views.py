from http import HTTPStatus
from typing import List, Optional

import os
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

@af_requests_bp.route("/output/<file>/", methods=["GET"])
def get_simulation_summary(file: str):
    request_uuid = request.args['requestId']
    #return df_json_response()
    overview_file_result = service.read_DSSAT_overview_file(file, request_uuid)
    return overview_file_result

@af_requests_bp.route("/<request_uuid>/result.zip")
def download_result(request_uuid: str):
    """Download file result of analysis request as zip file"""

    request_folder = os.path.join(config.ROOT_DATA_FOLDER_DSSAT, request_uuid)
    request_file = os.path.join(request_folder, 'result.zip')

    if not os.path.exists(request_file):
        error_response = api_models.ErrorResponse(errorMsg="Simulation Result file not found")
        return json_response(error_response, HTTPStatus.NOT_FOUND)

    request_uuid_without_hyphens = request_uuid.replace("-", "")
    download_name = f"{request_uuid_without_hyphens}.zip"

    return send_from_directory(request_folder, "result.zip", as_attachment=True, download_name=download_name)

@af_requests_bp.route("/", methods=["GET"])
def list():
    """Create request object based on body params"""
    query_params = api_models.AnalysisRequestListQueryParameters(**request.args)

    analyses, total_count = service.query(query_params)

    # DTOs for api response
    analysis_request_dtos = []

    for analysis in analyses:
        columns = [m.key for m in analysis.__table__.columns]
        #print(columns)
        analysis_request_dtos.append(_map_analysis(analysis))

    response = api_models.SimulationRequestListResponse(  
        metadata=api_models.create_metadata(query_params.page, query_params.pageSize, total_count),
        result=api_models.SimulationRequestListResponseResult(data=analysis_request_dtos),
    )

    return json_response(response, HTTPStatus.OK)

def _map_analysis(analysis):
    """Maps the db result to the Result model."""

    req = analysis.simulation_req
    req_dto = api_models.CropSimulationRequest(
        requestId=req.uuid,
        requestorId=req.requestor_id,
        crop=req.crop,
        institute=req.institute,
        analysisType=req.type,
        experimentname = req.experimentname,
        status=req.status,
        statusMessage=req.msg,
        createdOn=req.creation_timestamp,
        modifiedOn=req.modification_timestamp,
    )

    if req.status == Status.DONE:
        req_dto.resultDownloadRelativeUrl = config.get_result_download_url(req.uuid)

    return req_dto
