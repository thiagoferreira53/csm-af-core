#!/usr/bin/env python3
import abc
import argparse
import datetime
import json
import os
import subprocess
import sys
from os import path

from pipeline.analysis_request import DSSAT_AnalysisRequest
from pipeline.db.core import DBConfig
from pipeline.dpo import ProcessData
from pipeline.exceptions import InvalidAnalysisRequest

from pipeline.db import services as db_services
from pipeline import config
from pydantic import ValidationError


class Analyze(abc.ABC):
    dpo_cls: ProcessData = None
    engine_script: str = ""

    def __init__(self, analysis_request: DSSAT_AnalysisRequest, *args, **kwargs):
        """Constructor.

        Constructs analysis db record and other required objects.

        Args:
            analysis_request: Object with all required inputs to run analysis.
        """
        self.analysis_request = analysis_request

        self.db_session = DBConfig.get_session()

        self.dssat_path = config.get_dssat_path()



def get_analyze_object(analysis_request: DSSAT_AnalysisRequest, session=None):
    """Returns the configured Analyze object based on engine name"""

    engine_script = config.get_analysis_engine_script('dssat')
    kls = config.get_analyze_class(engine_script)
    return kls(analysis_request, engine_script=engine_script)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process input data to feed into analytical engine")

    parser.add_argument("--request_file", help="File path for analysis request")

    args = parser.parse_args()

    request_file ='/Users/thiagoferreira53/Desktop/EBS_templates/new.JSON' #temporary for testing

    if path.exists(request_file):
        with open(request_file) as f:
            try:
                analysis_request: DSSAT_AnalysisRequest = DSSAT_AnalysisRequest(**json.load(f))
                #print(analysis_request)
            except ValidationError as e:
                raise InvalidAnalysisRequest(str(e))
    else:
        raise InvalidAnalysisRequest(f"Request file {request_file} not found")

    sys.exit(get_analyze_object(analysis_request).run())