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
    req = db_models.Request_Simulation(
        uuid=analysis_uuid,
        category = "Crop Growth Simulation",
        institute=request_params.institute,
        crop=request_params.crop,
        experimentname=request_params.experimentname,
        type=request_params.analysisType,
        requestor_id=request_params.requestorId,
        status="PENDING",
    )

    additionalInfo = {"data_sources":
    [{'source' : request_params.dataSource, 'url' : request_params.dataSourceUrl, 'token' : request_params.dataSourceAccessToken}]}


    simulation = db_models.Simulation_Data(
        simulation_req=req,
        name=analysis_uuid,
        creation_timestamp=datetime.utcnow(),
        experimentname=request_params.experimentname,
        status="IN-PROGRESS",
        crop=request_params.crop,
#        analysis_request_data=req_data.dict(),
#        additional_info=additionalInfo
    )

    with db.session.begin():
        db.session.add(simulation)
        celery_util.send_task(
            process_name="prepare_simulation",
            args=(
                req.uuid,
                json.loads(request_params.json()),
            ), #queue="DSSAT",
        )
    return simulation


def read_DSSAT_overview_file(file_name,  request_id):
    data_request = celery_util.send_task_get(process_name="get_DSSAT_output_file", args=(file_name, request_id,), queue="DSSAT", routing_key="DSSAT")
    print(data_request)
    return data_request

def get_DSSAT_simulations(requestor_id):
    data_request = celery_util.send_task(process_name="get_DSSAT_simulation_list", args=(requestor_id,), queue="DSSAT")
    return data_request



def __query_simulation(query_params: api_models.AnalysisRequestListQueryParameters):

    query = db_models.Simulation_Data.query.join(db_models.Request_Simulation)

    if query_params.requestorId:
        query = query.filter(db_models.Request_Simulation.requestor_id == query_params.requestorId)

    elif query_params.crop:
        query = query.filter(db_models.Request_Simulation.crop == query_params.crop)

    elif query_params.institute:
        query = query.filter(db_models.Request_Simulation.institute == query_params.institute)

    elif query_params.status:
        query = query.filter(db_models.Request_Simulation.status == query_params.status)

    else:
        print("no args")

    return query


def query(query_params: api_models.AnalysisRequestListQueryParameters):

    query = __query_simulation(query_params)

    total_count = query.count()

    # Get latest requests first
    # query = query.order_by(db_models.Request_Simulation.creation_timestamp.desc())

    # AnalysisRequestListQueryParameters have default page and pageSize
    query = query.limit(query_params.pageSize).offset(query_params.page * query_params.pageSize)

    simulation_requests = query.all()

    return simulation_requests, total_count