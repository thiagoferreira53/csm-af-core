from af_task_orchestrator.af.pipeline.data_reader.models.dssat_enum import DataSource, DataType
from pydantic import BaseModel


#this might change later on to allow multiple locations, values, etc
class DSSAT_AnalysisRequest(BaseModel):
    requestId: str
    dataSource: DataSource
    dataType: DataType
    crop: str
    soil_id_num: str
    startDate: str
    endDate: str
    startDOY: str
    startDOYSim: str
    FertDOY: str
    endDOY: str
    Iresidue: str
    Iroot: str
    Initro: str
    NitroFert: str
    IrrType: str
    CultivarID: str
    Cultivar: str
    outputFolder: str
    latitude : str
    longitude : str

