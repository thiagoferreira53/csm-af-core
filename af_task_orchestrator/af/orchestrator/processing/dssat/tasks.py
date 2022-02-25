from http import HTTPStatus

from af_task_orchestrator.af.orchestrator import dssatutil
from af_task_orchestrator.af.orchestrator.app import app
from jobs_api.common.responses import json_response
from af_task_orchestrator.af.pipeline import analyze as pipeline_analyze
from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest

# from af.orchestrator.base import StatusReportingTask


@app.task(name="run_dssat", queue="DSSAT")  # , base=StatusReportingTask)
def run_dssat(params: dict):
    """params is a dict that should contain the following:

    requestId:  the request uuid
    """
    requestId = params.get("requestId")
    print('dssat/tasks/', requestId)

    analysis_request = DSSAT_AnalysisRequest(**params)

    analyze_object = pipeline_analyze.get_analyze_object(analysis_request)
    input_files = analyze_object.pre_process()


@app.task(name="get_summary", queue="DSSAT")  # , base=StatusReportingTask)
def get_summary():
    """params is a dict that should contain the following:

    requestId:  the request uuid
    """
    analyze_object = pipeline_analyze.get_analyze_object()


