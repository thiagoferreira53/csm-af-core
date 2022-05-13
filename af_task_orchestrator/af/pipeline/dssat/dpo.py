import json
import os
import re
from datetime import datetime
import glob
import numpy

from af_task_orchestrator.af.pipeline.dssat.services import get_weather_data, run_dssat_simulation, get_crop_data, write_fileX
from af_task_orchestrator.af.pipeline.dpo import ProcessData
from af_task_orchestrator.af.pipeline import config
from af_task_orchestrator.af.pipeline.job_data import JobData


class DSSATProcessData(ProcessData):

    def __init__(self, analysis_request):
        super().__init__(analysis_request)

    def __get_job_name(self):
        # TODO: put this in ProcessData
        return f"{self.analysis_request.requestId}"



    def execute_simulation(self):

        self.job_folder = self.get_job_folder(self.__get_job_name())

        job_data = JobData()
        job_data.job_name = self.__get_job_name()
        job_data.job_file = os.path.join(self.job_folder, f"{self.__get_job_name()}.json") #I might write outputs here

        crop = self.analysis_request.crop

        data_parameters = self.analysis_request.parameters

        path_dssat = config.DSSAT_P

        weather_name = 'AAAA'
        for location in data_parameters[0].keys():
            start_date = data_parameters[0][location]['startdate']
            end_date = data_parameters[0][location]['enddate']
            latitude = data_parameters[0][location]['latitude']
            longitude = data_parameters[0][location]['longitude']
            get_weather_data(self.db_session, start_date, end_date, latitude, longitude, self.job_folder, weather_name)
            new = int(weather_name, 36) + 1
            weather_name = numpy.base_repr(new, 36)

        write_fileX(self.db_session, self.job_folder, self.analysis_request)

        run_dssat_simulation(self.job_folder, path_dssat, crop)

        return job_data


    def run(self):
        """Preprocess input data for DSSAT Crop Modeling Simulations"""
        return [self.execute_simulation()]

