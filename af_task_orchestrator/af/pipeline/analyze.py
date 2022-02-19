#!/usr/bin/env python3
import abc
import argparse
import json
import sys
from os import path

from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest
from af_task_orchestrator.af.pipeline.db.core import DBConfig
from af_task_orchestrator.af.pipeline.dpo import ProcessData
from af_task_orchestrator.af.pipeline.exceptions import InvalidAnalysisRequest

from af_task_orchestrator.af.pipeline import config
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

    def get_process_data(self, analysis_request, *args, **kwargs):
        """Get the associated ProcessData object for this Analyze"""
        return self.dpo_cls(analysis_request)

    def pre_process(self):
        job_input_files = self.get_process_data(self.analysis_request).run()
        return job_input_files

    def get_engine_script(self):
        return self.engine_script



def get_analyze_object(analysis_request: DSSAT_AnalysisRequest, session=None):
    """Returns the configured Analyze object based on engine name"""
    #if not session:
    #    session = DBConfig.get_session()

    #analysis_engine_meta = db_services.get_analysis_config_meta_data(
    #    session, analysis_request.analysisConfigPropertyId, "engine")
    #engine_script = config.get_analysis_engine_script(analysis_engine_meta.value)
    engine_script = config.get_analysis_engine_script('dssat')  #temporary for testing

    kls = config.get_analyze_class(engine_script)
    return kls(analysis_request, engine_script=engine_script)


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

    sys.exit(get_analyze_object(analysis_request).run())