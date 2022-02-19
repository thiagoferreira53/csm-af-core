from af_task_orchestrator.af.orchestrator import config
from af_task_orchestrator.af.orchestrator.app import app
from af_task_orchestrator.af.orchestrator.base import ResultReportingTask, StatusReportingTask
from af_task_orchestrator.af.pipeline import analyze as pipeline_analyze
from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest



@app.task(name="analyze", base=StatusReportingTask)
def analyze(request_id: str, request_params):
    """Analyze taks run the analysis engine for given task request parameters.

    Based on the type of executor whether it is Celery or Slurm, the method submits the task
    to respective executor.

    Args:
        request_id: Id of the request to process.
        request_params: Dict object with request parameters passed to analysis module.
    """

    output_folder = config.get_analysis_request_folder(request_id)

    analysis_request = DSSAT_AnalysisRequest(requestId=request_id, outputFolder=output_folder, **request_params)

    # TODO: Condition to check executor is celery, If executor is slurm, submit analyze script as sbatch
    # pipeline_analyze.Analyze(analysis_request).run()
    # let's call init_analyze with the analysis_request object

    pre_process.delay(request_id, analysis_request)


@app.task(name="pre_process", base=StatusReportingTask)
def pre_process(request_id, analysis_request):
    analyze_object = pipeline_analyze.get_analyze_object(analysis_request)
    input_files = analyze_object.pre_process()
    # engine = analyze_object.get_engine_script()

    results = []  # results initially empty
    args = request_id, analysis_request, input_files, results

    engine = analyze_object.get_engine_script()
    if engine == "asreml":
        app.send_task("run_asreml_analyze", args=args, queue="ASREML")
    if engine == "dssat":
        app.send_task("run_asreml_analyze", args=args, queue="DSSAT")
    if engine == "sommer":
        app.send_task("run_sommer_analyze", args=args)


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


