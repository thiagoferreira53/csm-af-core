from af_task_orchestrator.af.pipeline.analysis_request import DSSAT_AnalysisRequest
from af_task_orchestrator.af.pipeline.analyze import Analyze
from af_task_orchestrator.af.pipeline.job_data import JobData

from .dpo import DSSATProcessData


class DSSATAnalyze(Analyze):

    dpo_cls = DSSATProcessData
    engine_script = "dssat"

    def __init__(self, analysis_request: DSSAT_AnalysisRequest, *args, **kwargs):
        super().__init__(analysis_request=analysis_request, *args, **kwargs)


    def get_cmd(self, job_data, analysis_engine=None):
        return ["dssat", job_data.job_file]

    def finalize(self, gathered_objects):
        pass

    def process_job_result(self, job_result: JobData, gathered_objects: dict = None):
        pass