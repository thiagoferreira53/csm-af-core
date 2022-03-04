from datetime import datetime
from enum import Enum
from typing import List, Optional

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

class CropSimulationRequest(AfBaseModel):
    requestId: str = None
    requestorId: Optional[str] = None
    crop: Optional[str] = Field(None, description="Name of the crop")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    analysisType: Optional[AnalysisType] = None
    model: str
    latitude: str
    longitude: str
    startdate: str
    enddate: str
    irrtype: str
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
    crop: Optional[str] = Field(None, description="Name of the crop")
    requestorId: Optional[str] = Field(None, description="Id of the user who submits analysis request.")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    analysisType: Optional[AnalysisType] = None
    model: str
    latitude: str
    longitude: str
    startdate: str
    enddate: str
    irrtype: str
