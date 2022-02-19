from af_task_orchestrator.af.pipeline import analyze as pipeline_analyze
from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest

import json
request_file = '/Users/thiagoferreira53/Desktop/EBS_templates/new.JSON'  # temporary for testing

with open(request_file) as f:
        request_params = json.load(f)

analysis_request = DSSAT_AnalysisRequest(requestId=1, outputFolder='/Users/thiagoferreira53/Desktop/EBS_templates', **request_params)


analyze_object = pipeline_analyze.get_analyze_object(analysis_request)
input_files = analyze_object.pre_process()
#print("tasks", input_files)

engine = analyze_object.get_engine_script()

#print("tasks", engine)