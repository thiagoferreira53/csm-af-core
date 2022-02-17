from pipeline.db.services import get_daily_weather_info, get_mega_env_id, get_soil_id, get_carbon_value
from pipeline.db.services import get_soil_water_value, get_init_residue_mass_value, get_init_root_mass_value
from pipeline.db.services import get_soil_nitrogen_value, get_plating_date_winter_wheat, get_plating_date_spring_wheat
from pipeline.db.services import get_nitrogen_app_irrigated_value, get_nitrogen_app_rainfed_value

import os
import csv
import re
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import glob


def get_weather_data(dbsession, job_id: int, start_date: str, end_date: str, latitude: float, longitude: float, path: str):
    """
    Creates a weather file (.WHT) for DSSAT crop growth simulations
    """
    df = get_daily_weather_info(dbsession, start_date, end_date, latitude, longitude)
    #print(type(df), df.count())
    for r in range(df.count()):
        if not os.path.exists(path + str(latitude) + '_' + str(longitude) + '.WTH'):
            weather = open(path + str(latitude) + '_' + str(longitude) + '.WTH', 'w')
            write_WTH = csv.writer(weather, delimiter=' ')
            weather.write("%s %7s %7s \n" % ('@INSI', 'LAT', 'LONG'))
            weather.write("%5s %7s %7s \n" % ('XXXX', latitude, longitude))
            weather.write("%5s %5s %5s %5s %5s\n" % ('@DATE', 'SRAD', 'TMAX', 'TMIN', 'RAIN'))
            weather.write("%05s %5.1f %5.1f %5.1f %5.1f\n" % (
                str(df[r][0])[2:4] + str('{:03}'.format(df[r][0].timetuple().tm_yday)),
                df[r][4], df[r][2], df[r][3], df[r][1]))


#defining some parameters for simulation
ME_List = {'CultivarID': ['IB0008','IB0009','IB0011','IB0012','IB0015','IB0017','IB0018','IB0019','IB0021','IB0022',
                       'IB0023','IB0024'],
        'Cultivar': ["ME1-PBW343", "ME2A-Kubsa", "ME3-Alondra", "ME4A-Bacanora", "ME5A-Kanchan", "ME6-Saratovskaya",
                    "ME7-Pehlivan", "ME8A-HalconSNA", "ME9-Bacanora", "ME10-Bezostaya", "ME11-Brigadier", "ME12-Gerek79"]
        }

MegaEnvironments = pd.DataFrame(ME_List, columns = ['CultivarID', 'Cultivar'])


def get_crop_data(dbsession, job_id: int, start_date: str, end_date: str, latitude: float, longitude: float, path: str, IR: bool):
    """
    Creates a experiment file (FileX) for DSSAT crop growth simulations
    """
    ME = get_mega_env_id(dbsession, latitude, longitude).scalar()  # ME
    soil = int(get_soil_id(dbsession, latitude, longitude).scalar())  # soil
    carbon = get_carbon_value(dbsession, latitude, longitude).scalar()  # carbon
    soil_water = get_soil_water_value(dbsession, latitude, longitude).scalar()  # soil water content
    init_residue = int(get_init_residue_mass_value(dbsession, latitude, longitude).scalar() or 0)  # no val
    init_root = int(get_init_root_mass_value(dbsession, latitude, longitude).scalar() or 0)  # no val
    nitr = get_soil_nitrogen_value(dbsession, latitude, longitude).scalar()
    pdate_winter = get_plating_date_winter_wheat(dbsession, latitude, longitude).scalar()
    pdate_spring = get_plating_date_spring_wheat(dbsession, latitude, longitude).scalar()
    nitr_irr = int(get_nitrogen_app_irrigated_value(dbsession, latitude, longitude).scalar())
    nitr_rf = int(get_nitrogen_app_rainfed_value(dbsession, latitude, longitude).scalar())

    CultivarID = MegaEnvironments[
        MegaEnvironments['Cultivar'].str.match(rf"^{ME}-[a-zA-Z0-9]*|{ME}[A-Z]-[a-zA-Z0-9]*") == True].CultivarID.item()
    Cultivar = MegaEnvironments[
        MegaEnvironments['Cultivar'].str.match(rf"^{ME}-[a-zA-Z0-9]*|{ME}[A-Z]-[a-zA-Z0-9]*") == True].Cultivar.item()

    if (int(re.sub('\D', '', ME)) >= 9):
        platDate = int(pdate_spring)
    else:
        platDate = int(pdate_winter)

    dt = datetime.strptime(start_date, '%Y/%m/%d')
    startDateMonth = str(dt.year) + "/" + str(platDate).zfill(2) + "/01"
    startDateSim = str(datetime.strptime(startDateMonth, '%Y/%m/%d').date() - timedelta(60))
    AutoEndDateSim = str(datetime.strptime(startDateMonth, '%Y/%m/%d').date() + timedelta(30))
    FertDate = str(datetime.strptime(startDateMonth, '%Y/%m/%d').date() + timedelta(40))
    startDOY = startDateMonth[2:4] + pd.Series(pd.to_datetime(startDateMonth)).dt.dayofyear.map("{:003}".format).values[0]
    startDOYSim = startDateSim[2:4] + pd.Series(pd.to_datetime(startDateSim)).dt.dayofyear.map("{:003}".format).values[0]
    FertDOY = startDateMonth[2:4]+pd.Series(pd.to_datetime(FertDate)).dt.dayofyear.map("{:003}".format).values[0]

    endDOY = AutoEndDateSim[2:4] + pd.Series(pd.to_datetime(AutoEndDateSim)).dt.dayofyear.map("{:003}".format).values[0]

    tmplName = "DSSAT_Standard.tmpl"

    fileTmpl = path + tmplName

    tmpl = open(fileTmpl, 'r')

    now = datetime.now()

    DSSATjson = tmpl.read()
    DSSATjson = re.sub("\[RQTS\]", str(now), DSSATjson)
    DSSATjson = re.sub("\[RQID\]", '1000000', DSSATjson)
    DSSATjson = re.sub("\[RRID\]", 'test', DSSATjson)

    DSSATjson = re.sub("\[CROP\]", 'wheat', DSSATjson)   #update
    DSSATjson = re.sub("\[SOIL_ID\]", str(soil), DSSATjson)
    DSSATjson = re.sub("\[START_DATE\]", start_date, DSSATjson)
    DSSATjson = re.sub("\[END_DATE\]", end_date, DSSATjson)
    DSSATjson = re.sub("\[START_DOY\]", str(startDOY), DSSATjson)
    DSSATjson = re.sub("\[START_SIM\]", str(startDOYSim), DSSATjson)
    DSSATjson = re.sub("\[FERT_DOY\]", str(FertDOY), DSSATjson)
    DSSATjson = re.sub("\[AEND_DOY\]", str(endDOY), DSSATjson)
    DSSATjson = re.sub("\[INIT_RES\]", str(init_residue), DSSATjson)
    DSSATjson = re.sub("\[ROOT_WT\]", str(init_root), DSSATjson)
    DSSATjson = re.sub("\[INIT_NITRO\]", str(nitr), DSSATjson)
    if IR == "TRUE":
        DSSATjson = re.sub("\[NITRO\]", str(nitr_irr), DSSATjson)
        DSSATjson = re.sub("\[IRR_TYPE\]", "A", DSSATjson)
    else:
        DSSATjson = re.sub("\[NITRO\]", str(nitr_rf), DSSATjson)
        DSSATjson = re.sub("\[IRR_TYPE\]", "R", DSSATjson)
    DSSATjson = re.sub("\[CULT_ID\]", CultivarID, DSSATjson)
    DSSATjson = re.sub("\[CULT_NAME\]", Cultivar, DSSATjson)
    DSSATjson = re.sub("\[DSSAT_WORKDIR\]", path, DSSATjson)

    DSSATjsonPath = path + str(job_id) + "test.JSON"   #rename
    DSSATjsonFile = open(DSSATjsonPath, 'w')
    DSSATjsonFile.write(DSSATjson)
    DSSATjsonFile.close()

    return DSSATjsonPath

def create_cultivar_param():
    """
    Creates cultivar file for Crop Growth Simulations.
    """

def run_dssat_simulation(path, path_dssat_exe):
    """
    Executes DSSAT.
    """
    os.chdir(path)

    #rename weather file for simulation
    weather_file = glob.glob('./*.WTH')
    os.rename(path+"/"+weather_file[0],path+'/RRRR.WTH')



    subprocess.call([path_dssat_exe+'dscsm048', 'B',
                     'BatchFile.v48'])

def get_simulation_predictions(job_id: int, prediction_result_file_path: str):

    """
    Creates a list of Prediction sqlalchemy objects, by parsing the input sommer result file. Prediction model is already defined in db models.
    """

