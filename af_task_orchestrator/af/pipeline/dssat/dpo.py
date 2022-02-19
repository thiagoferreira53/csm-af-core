import json
import os
import re
from datetime import datetime
import glob

from af_task_orchestrator.af.pipeline.dssat.services import get_weather_data, run_dssat_simulation, get_crop_data
from af_task_orchestrator.af.pipeline.dpo import ProcessData
from af_task_orchestrator.af.pipeline import config


class DSSATProcessData(ProcessData):

    def __init__(self, analysis_request):
        super().__init__(analysis_request)

    def __get_job_name(self):
        # TODO: put this in ProcessData
        return f"{self.analysis_request.requestId}"


    def execute_simulation(self):

        job_folder = self.get_job_folder(self.__get_job_name())

        start_date = self.analysis_request.startDate
        end_date = self.analysis_request.endDate
        latitude = self.analysis_request.latitude
        longitude = self.analysis_request.longitude
        IR = self.analysis_request.IrrType
        path_dssat = config.DSSAT_P

        path_JSON_file = self.__create_files_from_input(start_date, end_date, latitude, longitude, job_folder, IR)

        self.__read_meta(path_JSON_file)

        self.__write_bash_DSSAT(job_folder)

        run_dssat_simulation(job_folder, path_dssat)

    def __read_meta(self, path) -> dict:
        with open(path, 'r') as j:
            request = j.read()

            obj = json.loads(request)

            if obj["metadata"]["requestCategory"] == "Standard_Data":
                self.__read_input_DSSAT_standard(obj, path)
            else:
                self.__read_input_DSSAT_custom(obj)

    def __create_files_from_input(self, start_date, end_date, latitude, longitude, path, IR):

        job_id = self.__get_job_name()

        get_weather_data(self.db_session, start_date, end_date, latitude, longitude, path)
        path_json = get_crop_data(self.db_session, start_date, end_date, latitude, longitude, path, IR)
        return path_json

    def __read_input_DSSAT_standard(self, obj, path_json) -> dict:

        #extract path to the json file
        path = os.path.split(path_json)[0]

        crop = obj["parameters"]["crop"]
        soil_id_num = obj["parameters"]["soil"]
        startDate = obj["parameters"]["startDate"]
        endDate = obj["parameters"]["endDate"]
        startDOY = obj["parameters"]["startDOY"]
        startDOYSim = obj["parameters"]["startSim"]
        FertDOY = obj["parameters"]["FertDOY"]
        endDOY = obj["parameters"]["AendDOY"]
        Iresidue = obj["parameters"]["iniRes"]
        Iroot = obj["parameters"]["rootWt"]
        Initro = obj["parameters"]["iniNitro"]
        NitroFert = obj["parameters"]["NitroFert"]
        IrrType = obj["parameters"]["Irrigation"]
        CultivarID = obj["parameters"]["cultivarID"]
        Cultivar = obj["parameters"]["cultivarName"]
        workdir = obj["parameters"]["workdirectory"]

        soil_id = "HN_GEN00" + str(soil_id_num).zfill(2)

        sd = datetime.strptime(startDate, '%Y/%m/%d')
        ed = datetime.strptime(endDate, '%Y/%m/%d')

        tmpl = open(config.TEMPLATES_FOLDER + '/whTemplate.SNX', 'r')
        fileX = tmpl.read()
        fileX = re.sub("ssssssssss", str(soil_id), fileX)
        fileX = re.sub("ppppS", "{:>5}".format(str(startDOY)), fileX)
        fileX = re.sub("iiiiS", "{:>5}".format(str(startDOYSim)), fileX)
        fileX = re.sub("ppppE", "{:>5}".format(str(endDOY)), fileX)
        fileX = re.sub("rrrr", "{:>4}".format("2150"), fileX)
        fileX = re.sub("wwww", "{:>4}".format("RRRR"), fileX)
        fileX = re.sub("inres", "{:>5}".format(str(Iresidue)), fileX)
        fileX = re.sub("rtwt", "{:>4}".format(str(Iroot)), fileX)
        fileX = re.sub("nitro", "{:>5}".format(str(Initro)), fileX)
        fileX = re.sub("fnn", "{:>5}".format("0"), fileX)
        fileX = re.sub("nnnnn", "{:>5}".format(str(ed.year - sd.year)), fileX)
        fileX = re.sub("Rco2p", "{:>5}".format("R 362"), fileX)
        fileX = re.sub("CultID", "{:>6}".format(CultivarID), fileX)
        fileX = re.sub("CultN", "{:<20}".format(Cultivar), fileX)
        fileX = re.sub("fertD", "{:>5}".format(str(FertDOY)), fileX)
        fileX = re.sub("scirm", "{:>5}".format(IrrType), fileX)

        #models = ['CSCER', 'WHAPS', 'CSCRP']
        models = ['CSCER', 'WHAPS']

        count = 0
        for i in models:
            count = count + 1
            fileX_gen = re.sub("model", "{:>5}".format(i), fileX)
            fileX_gen = re.sub("trtname", "{:<6}".format(i), fileX_gen)

            if int(NitroFert) <= 30:
                fileX_gen = re.sub("nit1", "{:>4}".format(str(int(NitroFert) / 2)), fileX_gen)
                fileX_gen = re.sub("nit2", "{:>4}".format(str(int(NitroFert) / 2)), fileX_gen)
            if int(NitroFert) > 30 and int(NitroFert) < 100:
                fileX_gen = re.sub("nit1", "{:>4}".format("30"), fileX_gen)
                fileX_gen = re.sub("nit2", "{:>4}".format(str(int(NitroFert) - 30)), fileX_gen)
            if int(NitroFert) >= 100:
                fileX_gen = re.sub("nit1", "{:>4}".format("80"), fileX_gen)
                fileX_gen = re.sub("nit2", "{:>4}".format(str(int(NitroFert) - 80)), fileX_gen)
                # fileX_gen = re.sub("nit3", "{:>5}".format(str((NitroFert - 80)/2)), fileX)

            DSSATjsonFile = open(path + "/RRRR010" + str(count) + ".WHX", 'w')
            DSSATjsonFile.write(fileX_gen)
            DSSATjsonFile.close()

    def __read_input_DSSAT_custom(self, obj, path_json) -> dict:
        # extract path to the json file
        path = os.path.split(path_json)[0]

        workdir = obj["parameters"]["workdirectory"]
        trt = obj["parameters"]["nTreatment"]
        cul = obj["parameters"]["cultivar"]
        exp = obj["parameters"]["experiment"]
        crop = obj["parameters"]["crop"]
        cropModel = obj["parameters"]["cropModel"]
        print(cropModel)

        name = exp.split(".")[0]

        print(name)
        expNam = re.findall("[a-zA-Z]+", exp.split(".")[0])

        expNum = re.findall("\d+", exp)[0]

        cultivarIds = cul.split()

        # Creat file X
        for f in cultivarIds:
            print("cul:" + f)
            tmpl = open(path + '/' + exp, 'r')
            fileX = tmpl.read()
            fileX = re.sub("\[cuID\]", f.split(":")[0], fileX)
            fileX = re.sub("\[cmID\]", cropModel, fileX)
            fileX = re.sub("\[cuName\]", f.split(":")[1], fileX)
            # print(fileX)
            DSSATjsonPath = path + "/" + "".join(expNam) + str(
                int(expNum) + cultivarIds.index(f) + 1) + "." + exp.split(".")[1]

            DSSATjsonFile = open(DSSATjsonPath, 'w')
            DSSATjsonFile.write(fileX)
            DSSATjsonFile.close()
        os.remove(path + '/' + exp)

    #function required to execute every simulation request
    def __write_bash_DSSAT(self, path):
        #print(path + '/BatchFile.v48')
        DSSATbatch = open(path + '/BatchFile.v48', 'w')
        DSSATbatch.write("$BATCH(%s)\n" % "Wheat".upper())
        DSSATbatch.write("!\n")
        DSSATbatch.write("! Directory    : %s\n" % path)
        DSSATbatch.write("! Command Line : %s B BatchFile.v48\n" % "/DSSAT48/dscsm048.exe")
        DSSATbatch.write("! Crop         : %s\n" % "Wheat")
        DSSATbatch.write("! Experiment   : %s\n" % "RRRR0100.WHX")
        DSSATbatch.write("! ExpNo        : %s\n" % "1")
        DSSATbatch.write("! Debug        : %s B BatchFile.v48\n" % "/DSSAT48/dscsm048.exe")
        DSSATbatch.write("!\n")
        DSSATbatch.write("%-93s %5s %6s %6s %6s %6s\n" % ("@FILEX", "TRTNO", "RP", "SQ", "OP", "CO"))
        for fileNames in glob.glob(path + "/*.WHX"):
            names = re.sub(".+\/", '', fileNames.rstrip())
            print("Creating fileX: " + names)
            DSSATbatch.write("%-93s %5s %6s %6s %6s %6s\n" % ("./" + names, 1, 1, 0, 0, 0))


    def run(self):
        """Preprocess input data for DSSAT Crop Modeling Simulations"""
        return [self.execute_simulation()]

