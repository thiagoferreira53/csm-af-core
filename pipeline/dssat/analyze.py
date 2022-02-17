from pipeline.dssat.dpo import DSSATProcessData
from pipeline.analyze import Analyze
from pipeline.analysis_request import DSSAT_AnalysisRequest


class DSSATAnalyze(Analyze):

    dpo_cls = DSSATProcessData
    engine_script = "dssat"

    def __init__(self, analysis_request: DSSAT_AnalysisRequest, *args, **kwargs):
        super().__init__(analysis_request=analysis_request, *args, **kwargs)
        print('abc', analysis_request)

    def get_cmd(self, job_data, analysis_engine=None):
        return ["dssat", job_data.job_file]