from pipeline.dssat.dpo import DSSATProcessData
from pipeline.analyze import Analyze

class DSSATAnalyze(Analyze):
    engine_script = "dssat"

    dpo_cls = DSSATProcessData
    dpo_cls