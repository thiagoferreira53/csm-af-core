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


class CropSimulationRequestParameters(BaseModel):
    requestId: str = None
    dataSource: DataSource
    dataSourceUrl: str = Field(..., description="Base API url of datasource instance.")
    dataSourceAccessToken: str = Field(..., description="Bearer token to access datasource.")
    crop: Optional[str] = Field(None, description="Name of the crop")
    requestorId: Optional[str] = Field(None, description="Id of the user who submits analysis request.")
    institute: Optional[str] = Field(None, description="Name of the institute for which the analysis is submitted.")
    createdOn: Optional[datetime] = None
    modifiedOn: Optional[datetime] = None
