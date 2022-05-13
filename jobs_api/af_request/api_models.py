from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from common.api_models import (
    AnalysisType,
    DataSource,
    ErrorResponse,
    Metadata,
    PaginationQueryParameters,
    Status,
    create_metadata,
)
from pydantic import BaseModel, Field

class AfBaseModel(BaseModel):
    status: Optional[Status] = None
    createdOn: Optional[datetime] = None
    modifiedOn: Optional[datetime] = None

class Job(AfBaseModel):

    jobId: str = None
    jobName: Optional[str] = None
    status: Optional[Status] = None
    statusMessage: Optional[str] = None

    startTime: Optional[str] = None
    endTime: Optional[str] = None

class Cultivar(BaseModel):
    simulationType: Optional[str]
    name: Optional[str]
    cultivarID: Optional[str]
    season: Optional[str]
    p1: Optional[str]
    p5: Optional[str]

class PlatingDate(BaseModel):
    simulationType: Optional[str]
    name: Optional[str]
    date: Optional[str]

class Fertlizer(BaseModel):
    simulationType: Optional[str]
    date: Optional[str]
    source: Optional[str]
    amount: Optional[str]
    method: Optional[str]

class Tillage(BaseModel):
    simulationType: Optional[str]
    date: Optional[str]
    type: Optional[str]
    depth: Optional[str]

class Irrigation(BaseModel):
    simulationType: Optional[str]
    date: Optional[str]
    amount: Optional[str]
    operation: Optional[str]

class InitialSoil(BaseModel):
    simulationType: Optional[str]
    layer: Optional[str]
    volumetric: Optional[str]
    ammoniumAmount: Optional[str]
    nitrate: Optional[str]

class SoilText(BaseModel):
    simulationType: Optional[str]
    layer: Optional[str]
    clay: Optional[str]
    silt: Optional[str]
    sand: Optional[str]
    organicCarbon: Optional[str]

class Location(BaseModel):
    latitude: Optional[str]
    longitude: Optional[str]
    cultivar: Optional[Cultivar]
    startdate: Optional[str]
    enddate: Optional[str]
    pdate: Optional[PlatingDate]
    fertilizerApp: Optional[list[Fertlizer]]
    tillage: Optional[list[Tillage]]
    irrigation: Optional[list[Irrigation]]
    initialSoil: Optional[list[InitialSoil]]
    soilText: Optional[list[SoilText]]

class CropSimulationRequest(AfBaseModel):
    requestId: str = None
    requestorId: Optional[str] = None
    crop: str = Field(None, description="Name of the crop")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    analysisType: Optional[AnalysisType] = None
    experimentname: str = None
    model: list = None
    parameters: list[Dict] = None
    status: Optional[Status] = None
    statusMessage: Optional[str] = None
    jobs: Optional[Job] = None
    createdOn: Optional[datetime] = None
    modifiedOn: Optional[datetime] = None
    resultDownloadRelativeUrl: Optional[str] = None

class CropSimulationRequestParameters(BaseModel):
    dataSource: DataSource
    dataSourceUrl: str = Field(..., description="Base API url of datasource instance.")
    dataSourceAccessToken: str = Field(..., description="Bearer token to access datasource.")
    crop: str = Field(None, description="Name of the crop")
    requestorId: Optional[str] = Field(None, description="Id of the user who submits analysis request.")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    analysisType: Optional[AnalysisType] = None
    experimentname: str = None
    model: list = None
    parameters: list[Dict] = None

