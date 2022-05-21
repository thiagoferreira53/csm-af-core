import os

os.environ['OUT_DIR'] = '/Users/thiagoferreira53/Desktop/CIMMYT/EBS/test_output_folder' #?# create env variable later on docker

ROOT_DATA_FOLDER = os.getenv("BA_DATA_DIR")

ROOT_DATA_FOLDER_DSSAT = os.getenv("OUT_DIR")

RESULT_DOWNLOAD_BY_REQUEST = "/test_output_folder/{request_id}/result.zip"


def get_analysis_request_folder(request_id: str) -> str:
    """Returns the shared data folder path for given request id."""

    if ROOT_DATA_FOLDER is None:
        return None
    return os.path.join(ROOT_DATA_FOLDER, "analysis", request_id)


def get_allowable_origins():
    allowable_origins = os.getenv("AFAPI_ALLOWABLE_ORIGINS")
    if allowable_origins is not None:
        allowable_origins = allowable_origins.split(";")
    return allowable_origins


def get_result_download_url(request_id: str):
    return RESULT_DOWNLOAD_BY_REQUEST.format(request_id=request_id)
