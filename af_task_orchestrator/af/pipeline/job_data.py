from dataclasses import dataclass, field

#from af.pipeline.data_reader.models import Occurrence  # noqa: E402; noqa: E402


@dataclass
class JobData:
    """Class for keeping data to run successful job like data file path and other related meta data for engines."""

    job_name: str = ""
    data_file: str = ""
    job_file: str = ""
    metadata_file: str = ""
    job_result_dir: str = ""

    #occurrences: list[Occurrence] = field(default_factory=list)
