#!/usr/bin/env python3

import argparse
import json
import os
import pathlib
from abc import ABC, abstractmethod
# from collections import OrderedDict
from os import path

from pydantic import ValidationError

from af_task_orchestrator.af.pipeline.db.core import DBConfig
from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest
from af_task_orchestrator.af.pipeline.exceptions import InvalidAnalysisRequest
from af_task_orchestrator.af.pipeline import config


class ProcessData(ABC):
    """Abstract class for ProcessData objects"""

    def __init__(self, analysis_request: DSSAT_AnalysisRequest, *args, **kwargs):
        """Constructor.

        Args:
            analysis_request: Object with all required inputs to run analysis.
        """

        self.analysis_request = analysis_request

        self.db_session = DBConfig.get_session()

        self.output_folder = config.OUT_DIR

    def get_job_folder(self, job_name: str) -> str:

        job_folder = os.path.join(self.output_folder, job_name)

        if not os.path.isdir(job_folder):
            # create parent directories
            os.makedirs(pathlib.Path(job_folder))

        return job_folder


    @abstractmethod
    def run(self):
        """This method should return the list of preprocessed input files info"""
        pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process input data to feed into analytical engine")

    parser.add_argument("--request_file", help="File path for analysis request")

    args = parser.parse_args()

    if path.exists(args.request_file):
        with open(args.request_file) as f:
            try:
                analysis_request: DSSAT_AnalysisRequest = DSSAT_AnalysisRequest(**json.load(f))
            except ValidationError as e:
                raise InvalidAnalysisRequest(str(e))
    else:
        raise InvalidAnalysisRequest(f"Request file {args.request_file} not found")

    ProcessData(analysis_request).run()
