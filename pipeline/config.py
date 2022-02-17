#move this file to the root of this folder (af/pipeline)


import os

#I must set this environment variable inside the docker-compose.yml
os.environ['AFDB_URL'] = 'postgresql://postgres:weather@localhost:5432/weather_data'

AFDB_URI = os.getenv("AFDB_URL")


UNIVERSAL_UNKNOWN = "NA"

ANALYZE_IMPLEMENTATIONS = {
    "asreml": "af.pipeline.asreml.analyze.AsremlAnalyze",
    "sommer": "af.pipeline.sommer.analyze.SommeRAnalyze",
    "dssat": "pipeline.dssat.analyze.DSSATAnalyze"
}

#SO FAR I'M NOT USING THE CODE BELLOW

def get_afdb_uri():
    return os.getenv("AFDB_URL")


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


#what is this doing?
def get_analyze_class(engine_name):
    """Gets the configured analyze class"""
    #
    kls = ANALYZE_IMPLEMENTATIONS.get(engine_name.lower())
    parts = kls.split(".")
    module = ".".join(parts[:-1])
    print('a ' + module)
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m