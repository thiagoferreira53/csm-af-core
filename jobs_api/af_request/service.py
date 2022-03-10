import json
import uuid as uuidlib
from datetime import datetime

import celery_util
import pydantic
from af_request import api_models
from af_request import models as db_models
from database import db


#class DataCoordinates(pydantic.BaseModel): #?# use?
#    latitude: list[api_models.Experiment] = None
#    traits: list[api_models.Trait] = None

def submit(request_params):
    """Submits analysis request to pipeline."""

    analysis_uuid = str(uuidlib.uuid4())
    req = db_models.Request_Simulation(
        uuid=analysis_uuid,
        category = "Crop Growth Simulation",
        institute=request_params.institute,
        crop=request_params.crop,
        type=request_params.analysisType,
        requestor_id=request_params.requestorId,
        status="PENDING",
    )

#    req_data = DataCoordinates(**request_params.dict())

    additionalInfo = {"data_sources":
    [{'source' : request_params.dataSource, 'url' : request_params.dataSourceUrl, 'token' : request_params.dataSourceAccessToken}]}


    simulation = db_models.Simulation_Data(
        simulation_req=req,
        name=analysis_uuid,
        creation_timestamp=datetime.utcnow(),
        status="IN-PROGRESS",
        model=request_params.model,
        latitude= request_params.latitude,
        longitude= request_params.longitude,
        startdate= request_params.startdate,
        enddate= request_params.enddate,
        irrtype= request_params.irrtype,
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