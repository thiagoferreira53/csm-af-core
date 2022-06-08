import os
import pandas as pd
from http import HTTPStatus
import json

from af_task_orchestrator.af.orchestrator import config
from af_task_orchestrator.af.orchestrator.app import app
from jobs_api.common.responses import json_response
from af_task_orchestrator.af.pipeline import analyze as pipeline_analyze
from af_task_orchestrator.af.pipeline import config as pipeline_config
from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest
from celery import current_task

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
    input_files = analyze_object.pre_process()
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

    #print('test request id', current_task.request.args[1])

@app.task(name="get_DSSAT_output_file", queue="DSSAT")
def get_DSSAT_output_file(file, request_id):
    output_folder = pipeline_config.OUT_DIR

    path_to_output_files = os.path.join(output_folder, request_id)

    if(file == 'summary'):
        summary_file = path_to_output_files + '/Summary.OUT'

        df = pd.read_csv(summary_file, skiprows=3, sep=r"\s+", index_col=False, engine='python')

        # funky way to get rid of @ from header
        cols = df.columns[1:]
        df = df.drop('EPCP', 1)
        df.columns = cols
        df.columns = df.columns.str.replace('.', '')
    
    if(file =='plantgro'): #this method works as well for Weather.OUT files
        plantgro_file = path_to_output_files + '/PlantGro.OUT'
        df_list = []
        count = 1 #for adding a new column that referes to the treatment number
        with open(plantgro_file, 'r+') as myfile:
            for myline in myfile:
                if '@YEAR' in myline:
                    bd = pd.DataFrame(columns = myline.split()) #get title
                    for myline in myfile:
                        if len(myline.strip()) == 0: #skip to the next if there is no more row for the treatment
                            break
                        bd.loc[len(bd)] = myline.split() #append rows to the dataframe
                    bd['TRT'] = count
                    count = count + 1
                    df_list.append(bd)

        #print(df_list)
        df = pd.concat(df_list, ignore_index=True)
        #print(df)

    output = json.dumps(df.to_dict(orient='list'))

    return output


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


