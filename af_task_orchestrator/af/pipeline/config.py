import os

#I must set this environment variable inside the docker-compose.yml
os.environ['AFDB_URL'] = 'postgresql://postgres:weather@localhost:5432/weather_data'
os.environ['DSSAT_PATH'] = '/Users/thiagoferreira53/Projects/dssat-csm-os-48/build/bin/dscsm048'
os.environ['TEMPLATES_FOLDER'] = '/Users/thiagoferreira53/Desktop/CIMMYT/EBS/template_folder'
os.environ['OUT_DIR'] = '/Users/thiagoferreira53/Desktop/CIMMYT/EBS/test_output_folder' #?# create env variable later on docker
#


AFDB_URI = os.getenv("AFDB_URL")
DSSAT_P = os.getenv('DSSAT_PATH')
TEMPLATES_FOLDER = os.getenv('TEMPLATES_FOLDER')
OUT_DIR = os.getenv("OUT_DIR")


UNIVERSAL_UNKNOWN = "NA"

ANALYZE_IMPLEMENTATIONS = {
    "asreml": "af-core.pipeline.asreml.analyze.AsremlAnalyze",
    "sommer": "af-core.pipeline.sommer.analyze.SommeRAnalyze",
    "dssat": "af_task_orchestrator.af.pipeline.dssat.analyze.DSSATAnalyze"
}

def get_afdb_uri():
    return os.getenv("AFDB_URL")


def get_dssat_path():
    return os.getenv("DSSAT_PATH")

def get_analysis_engine_script(engine_name: str):
    # This needs to configured from db
    engine = engine_name.lower()

    # Or this can just be defined by their respective Analyze classes
    if engine == "asreml":
        return "asreml"

    if engine in ["r - sommer", "sommer"]:
        return "sommer"
    if engine == "dssat":
        return "dssat"

def get_analyze_class(engine_name):
    """Gets the configured analyze class"""

    kls = ANALYZE_IMPLEMENTATIONS.get(engine_name.lower())
    parts = kls.split(".")
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m