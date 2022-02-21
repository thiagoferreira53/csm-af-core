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


class Property(AfBaseModel):
    propertyId: Optional[str] = None
    propertyCode: Optional[str] = None
    propertyName: Optional[str] = None
    label: Optional[str] = None
    statement: Optional[str] = None
    type: Optional[str] = None


class Experiment(BaseModel):
    experimentId: str
    experimentName: str


class Occurrence(BaseModel):
    occurrenceId: str
    occurrenceName: str
    locationId: Optional[str] = None
    locationName: Optional[str] = None


class Experiment(BaseModel):
    experimentId: str
    experimentName: str
    occurrences: Optional[list[Occurrence]] = None


class Trait(BaseModel):
    traitId: str
    traitName: str


class Job(AfBaseModel):

    jobId: str = None
    jobName: Optional[str] = None
    status: Optional[Status] = None
    statusMessage: Optional[str] = None

    startTime: Optional[str] = None
    endTime: Optional[str] = None


class AnalysisRequest(AfBaseModel):
    requestId: str = None
    requestorId: Optional[str] = None
    crop: Optional[str] = Field(None, description="Name of the crop")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    analysisType: Optional[AnalysisType] = None
    status: Optional[Status] = None
    statusMessage: Optional[str] = None
    jobs: Optional[List[Job]] = None
    experiments: Optional[list[Experiment]] = None
    traits: Optional[list[Trait]] = None
    createdOn: Optional[datetime] = None
    modifiedOn: Optional[datetime] = None
    resultDownloadRelativeUrl: Optional[str] = None
    analysisObjectiveProperty: Optional[Property] = Field(None, description="Property of analysis objective.")
    analysisConfigProperty: Optional[Property] = Field(None, description="Property of analysis configuration.")
    expLocAnalysisPatternProperty: Optional[Property] = Field(
        None, description="Property of experiment location analysis pattern."
    )
    configFormulaProperty: Optional[Property] = Field(None, description="Property of the formula to run the analysis.")
    configResidualProperty: Optional[Property] = Field(
        None, description="Property of the residual for the analysis model."
    )


class AnalysisRequestParameters(BaseModel):
    dataSource: DataSource
    dataSourceUrl: str = Field(..., description="Base API url of datasource instance.")
    dataSourceAccessToken: str = Field(..., description="Bearer token to access datasource.")
    crop: Optional[str] = Field(None, description="Name of the crop")
    requestorId: Optional[str] = Field(None, description="Id of the user who submits analysis request.")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    analysisType: Optional[AnalysisType] = AnalysisType.ANALYZE
    experiments: List[Experiment]
    occurrences: List[Occurrence]
    traits: List[Trait]
    analysisObjectivePropertyId: str = Field(..., description="Property Id of selected analysis objective.")
    analysisConfigPropertyId: str = Field(..., description="Property Id of selected analysis configuration.")
    expLocAnalysisPatternPropertyId: str = Field(
        ..., description="Property Id of selected experiment location analysis pattern."
    )
    configFormulaPropertyId: str = Field(..., description="Property Id of the formula to run the analysis.")
    configResidualPropertyId: str = Field(..., description="Property Id of the residual for the analysis model.")
    configPredictionPropertyIds: list[str] = Field([], description="Property Ids of predictions in the model.")


class AnalysisRequestListQueryParameters(PaginationQueryParameters):
    crop: Optional[str] = Field(None, description="Name of the crop")
    requestorId: Optional[str] = Field(None, description="Id of the user who submits analysis request.")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    status: Optional[Status] = None


class AnalysisRequestResponse(BaseModel):
    result: AnalysisRequest = None


class AnalysisRequestListResponseResult(BaseModel):
    data: Optional[List[AnalysisRequest]] = None


class AnalysisRequestListResponse(BaseModel):
    metadata: Optional[Metadata] = None
    result: Optional[AnalysisRequestListResponseResult] = None
