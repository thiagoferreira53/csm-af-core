import os

# TODO: come up with a way to have multiple data sources
# for each EBS or BRAPI

EBS_BASE_URL = os.getenv("B4R_API_BASE_URL")

BRAPI_BASE_URL = os.getenv("BRAPI_BASE_URL")

os.environ['AFDB_URL'] = 'postgresql://postgres:weather@localhost:5432/weather_data'
os.environ['DSSAT_PATH'] = '/Users/thiagoferreira53/Projects/dssat-csm-os-48/build/bin/dscsm048'

AFDB_URI = os.getenv("AFDB_URL")

ROOT_DATA_FOLDER = os.getenv("BA_DATA_DIR")


def get_analysis_request_folder(request_id: str) -> str:
    """Returns the shared data folder path for given request id."""

    if ROOT_DATA_FOLDER is None:
        return None
    analysis_request_folder = os.path.join(ROOT_DATA_FOLDER, "analysis", request_id)

    if os.path.exists(analysis_request_folder):
        return analysis_request_folder

    os.makedirs(analysis_request_folder)
    return analysis_request_folder
