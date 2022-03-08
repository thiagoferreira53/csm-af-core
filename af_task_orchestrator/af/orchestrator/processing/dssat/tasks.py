from http import HTTPStatus

from af_task_orchestrator.af.orchestrator import config
from af_task_orchestrator.af.orchestrator.app import app
from jobs_api.common.responses import json_response
from af_task_orchestrator.af.pipeline import analyze as pipeline_analyze
from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest

from af_task_orchestrator.af.orchestrator.base import StatusReportingTask, ResultReportingTask


@app.task(name="prepare_simulation", base=StatusReportingTask)
def prepare_simulation(request_id: str, request_params):

    output_folder = config.get_analysis_request_folder(request_id)

    analysis_request = DSSAT_AnalysisRequest(requestId=request_id, outputFolder=output_folder, **request_params)


    pre_process.delay(request_id, analysis_request)

    #analyze_object = pipeline_analyze.get_analyze_object(analysis_request)
    #input_files = analyze_object.pre_process()
    #engine = analyze_object.get_engine_script()


@app.task(name="pre_process", base=StatusReportingTask)
def pre_process(request_id, analysis_request):
    analyze_object = pipeline_analyze.get_analyze_object(analysis_request)
    input_files = analyze_object.pre_process() #gotta change this shit
    engine = analyze_object.get_engine_script()
    results = []  # results initially empty
    args = request_id, analysis_request, input_files, results
    
    engine = analyze_object.get_engine_script()
    if engine == "asreml":
        app.send_task("run_asreml_analyze", args=args, queue="ASREML")
    if engine == "sommer":
        app.send_task("run_sommer_analyze", args=args)
    if engine == "dssat":
        app.send_task("run_dssat_analyze", args=args, queue="DSSAT")


@app.task(name="post_process", base=StatusReportingTask)
def post_process(request_id, analysis_request, results, gathered_objects=None):

    result, results = results[0], results[1:]

    if gathered_objects is None:
        gathered_objects = {}

    analyze_object = pipeline_analyze.get_analyze_object(analysis_request)
    gathered_objects = analyze_object.process_job_result(result, gathered_objects)

    # process the results here
    if not results:
        done_analyze.delay(request_id, analysis_request, gathered_objects)
    else:
        post_process.delay(request_id, analysis_request, results, gathered_objects)


@app.task(name="done_analyze", base=ResultReportingTask)
def done_analyze(request_id, analysis_request, gathered_objects):
    # this is the terminal task to report DONE in tasks
    _ = pipeline_analyze.get_analyze_object(analysis_request).finalize(gathered_objects)



#testing
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

#testing
@app.task(name="get_summary", queue="DSSAT")  # , base=StatusReportingTask)
def get_summary():
    """params is a dict that should contain the following:

    requestId:  the request uuid
    """
    analyze_object = pipeline_analyze.get_analyze_object()


