from typing import Dict, List
from af_task_orchestrator.af.pipeline.data_reader.models.dssat_enum import DataSource, DataType
from pydantic import BaseModel


#this might change later on to allow multiple locations, values, etc
class DSSAT_AnalysisRequest(BaseModel):
    requestId: str
    dataSource: DataSource
#    dataType: DataType
    dataSourceAccessToken: str
    experimentname : str
    crop: str
    model: list
    parameters: list[Dict]


