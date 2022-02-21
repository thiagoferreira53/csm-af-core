import subprocess


def get_container_inputs_dir():
    return "/home/dssat/inputs"

def get_dssat_command(input_job_file_name, input_data_file_name):
    inputs_dir = get_container_inputs_dir()
    return ["dssat", f"{inputs_dir}/{input_job_file_name}", f"{inputs_dir}/{input_data_file_name}"]


def run_dssat(input_job_file_name, input_data_file_name):
    """
    run_dssat:

    Returns:
        raw_ouput:str

    Raises:

    """
    command = get_dssat_command(input_job_file_name, input_data_file_name)
    return subprocess.check_output(command, shell=False)

