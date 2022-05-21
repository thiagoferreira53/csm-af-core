from af_task_orchestrator.af.pipeline.db.services import get_daily_weather_info, get_mega_env_id_wheat, get_soil_id, get_carbon_value
from af_task_orchestrator.af.pipeline.db.services import get_soil_water_value, get_init_residue_mass_value, get_init_root_mass_value
from af_task_orchestrator.af.pipeline.db.services import get_soil_nitrogen_value, get_plating_date_winter_wheat, get_plating_date_spring_wheat
from af_task_orchestrator.af.pipeline.db.services import get_nitrogen_app_irrigated_value, get_nitrogen_app_rainfed_value
from af_task_orchestrator.af.pipeline import utils


import os
import csv
import re
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import glob
import numpy

def get_weather_data(dbsession, start_date: str, end_date: str, latitude: float, longitude: float, path: str, weather_name: str):
    """
    Creates a weather file (.WHT) for DSSAT crop growth simulations
    """
    df = get_daily_weather_info(dbsession, start_date, end_date, latitude, longitude)
    #print(type(df), df.count())

    weather_file_output = path + '/' + weather_name + '.WTH'

    for r in range(df.count()):
        if not os.path.exists(weather_file_output):
            weather = open(weather_file_output, 'w')
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


def write_fileX(dbsession, path, analysis):

    year= '1980' #standard value / always start with 80's cause it is a 30 year run (1980-2010)

    crop = analysis.crop
    print(analysis)

    data = analysis.parameters

    if crop == 'wheat':
        ext = 'WH'
    elif crop == 'rice':
        ext = 'RI'
    elif crop == 'maize':
        ext = 'MZ'

    count = 0
    with open(path + '/ECSM' + year[2:4] + '01.' + ext + 'X', 'w') as f:
        # headers
        f.write('*EXP. DETAILS: EBS Crop Modeling System (ECSM)\n\n')
        f.write("*GENERAL\n@PEOPLE\nThiago Berton Ferreira, Diego Pequeno, Stefan Einarson, Jeff Melkonian\n")
        f.write("@ADDRESS\n-99\n@SITE\n-99\n")
        f.write("@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........\n")
        f.write(
            "{:>7} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}\n\n".format("-99", "-99", "-99", "-99", "-99",
                                                                                     "-99", "-99", "-99", "-99", "-99"))
        f.write('*TREATMENTS                        -------------FACTOR LEVELS------------\n')
        f.write("@N R O C TNAME.................... CU FL SA IC MP MI MF MR MC MT ME MH SM\n")

        trt_list = list(data[0].keys())
        for model in range(len(analysis.model)):
            for trt_name in data[0].keys():
                index = trt_list.index(trt_name) + 1
                count = count + 1
                f.write(
                    "{:>2} {:>1} {:>1} {:>1} {:<25} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2}\n"
                                                 # tname                               (CU)   (FL)      (IC)   (MP)  (MI)
                        .format(count, 1, 1, 0, trt_name + '-' + analysis.model[model], index, index, 0, index, index, index,
                                # (MF)
                                index, 0, 0, 0, 0, 0, count))

        # cultivar header
        count = 0
        f.write("\n*CULTIVARS\n@C CR INGENO CNAME\n")
        for exp in data[0].keys():
            cultivar = data[0][exp]['cultivar']['simulationType']
            if cultivar == 'Standard':
                ME = get_mega_env_id_wheat(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar()  # ME
                cultivarID = MegaEnvironments[
                    MegaEnvironments['Cultivar'].str.match(
                        rf"^{ME}-[a-zA-Z0-9]*|{ME}[A-Z]-[a-zA-Z0-9]*") == True].CultivarID.item()
                cultivarName = MegaEnvironments[
                    MegaEnvironments['Cultivar'].str.match(
                        rf"^{ME}-[a-zA-Z0-9]*|{ME}[A-Z]-[a-zA-Z0-9]*") == True].Cultivar.item()
            else:
                cultivarID = data[0][exp]['cultivar']['cultivarId']
                cultivarName = data[0][exp]['cultivar']['name']
            count = count + 1
            f.write(
                "{:>2} {:>2} {:>6} {:<25}\n".format(count, ext, cultivarID, cultivarName))


        # fields header
        f.write("\n*FIELDS\n")
        f.write("@L ID_FIELD WSTA....  FLSA  FLOB  FLDT  FLDD  FLDS  FLST SLTX  SLDP  ID_SOIL    FLNAME\n")
        count = 0
        weather_name = 'AAAA'
        for exp in data[0].keys():
            soil_name = list(data[0][exp]['soilText'][0].keys())[0]
            if data[0][exp]['soilText'][0][soil_name]['simulationType'] == 'Standard':
                soil_num = int(get_soil_id(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar())
                soil_id = "HN_GEN00" + str(soil_num).zfill(2)
            else:
                soil_id = soil_name
            count = count + 1
            f.write("{:>2} {:>8} {:<8} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:<3} {:>7} {:<1} {:<12}\n"
                    .format(count, str(count).zfill(8), weather_name, '-99', '-99', '-99', '-99', '-99', '-99', '-99',
                            '-99 ', soil_id, "-99"))
            new = int(weather_name, 36) + 1
            weather_name = numpy.base_repr(new, 36)

        f.write("@L ...........XCRD ...........YCRD .....ELEV .............AREA .SLEN .FLWR .SLAS FLHST FHDUR\n")

        count = 0
        for exp in data[0].keys():
            count = count + 1
            f.write(
                "{:>2} {:>15} {:>15} {:>9} {:>17} {:>5} {:>5} {:>5} {:>5} {:>5}\n".format(count, "-99", "-99", "-99",
                                                                                          "-99", "-99",
                                                                                          "-99", "-99", "-99", "-99"))
        count = 0
        # soil analysis header
        f.write("\n*SOIL ANALYSIS\n")
        f.write("@A SADAT  SMHB  SMPX  SMKE  SANAME\n")
        f.write(" 1 00001   -99   -99   -99  -99\n")
        f.write("@A  SABL  SADM  SAOC  SANI SAPHW SAPHB  SAPX  SAKE  SASC\n")
        f.write(" 1    15   -99   -99   -99   -99   -99   -99   -99   -99\n")

        # initial conditions
        f.write("\n*INITIAL CONDITIONS\n")
        for exp in data[0].keys():
            init_residue = int(get_init_residue_mass_value(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar() or 0)  # no val
            init_root = int(get_init_root_mass_value(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar() or 0)  # no val
            init_nitr = get_soil_nitrogen_value(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar()

            count = count + 1

            pdateInfo = data[0][exp]['pdate']
            if (pdateInfo['simulationType'] == 'Standard'):
                ME = get_mega_env_id_wheat(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar()  # ME
                if (crop == 'wheat' and int(re.sub('\D', '', ME)) >= 9):
                    pdate_spring = get_plating_date_spring_wheat(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar()
                    platDate = int(pdate_spring)

                elif (crop == 'wheat' and int(re.sub('\D', '', ME)) < 9):
                    pdate_winter = get_plating_date_winter_wheat(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar()
                    platDate = int(pdate_winter)
                pdate = str(year) + "/" + str(platDate).zfill(2) + "/01"
            else:
                pdate = pdateInfo['date']

            initial_date = str(datetime.strptime(pdate, '%Y/%m/%d').date() - timedelta(60))

            initial_julian = initial_date[2:4] + \
                             pd.Series(pd.to_datetime(initial_date)).dt.dayofyear.map("{:003}".format).values[0]
            f.write("@C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME\n")
            f.write("{:>2} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:<5}\n"
                    .format(count, ext, initial_julian, init_residue, "0", "1", "1", "-99", init_root, init_nitr, "0", "100", "-99",
                            "-99"))
            f.write("@C  ICBL  SH2O  SNH4  SNO3\n")
            initialSoilData = data[0][exp]['initialSoil'][0]
            for soil in initialSoilData.keys():
                if initialSoilData[soil]['simulationType'] == 'Standard' or initialSoilData[soil][
                    'simulationType'] == 'Potential':
                    f.write("{:>2} {:>5} {:>5} {:>5} {:>5}\n".format(count, '-99', '-99', '-99', '-99'))
                    break
                else:
                    f.write("{:>2} {:>5} {:>5} {:>5} {:>5}\n"
                            .format(count, initialSoilData[soil]["layer"], initialSoilData[soil]["volumetric"],
                                    initialSoilData[soil]["ammoniumAmount"], initialSoilData[soil]["nitrate"]))

        count = 0
        # plating details
        f.write("\n*PLANTING DETAILS\n")
        f.write(
            "@P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME\n")
        for exp in data[0].keys():
            count = count + 1
            pdateInfo = data[0][exp]['pdate']
            if (pdateInfo['simulationType'] == 'Standard'):
                if (crop == 'wheat' and int(re.sub('\D', '', ME)) >= 9):
                    pdate_spring = get_plating_date_spring_wheat(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar()
                    platDate = int(pdate_spring)

                elif (crop == 'wheat' and int(re.sub('\D', '', ME)) < 9):
                    pdate_winter = get_plating_date_winter_wheat(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar()
                    platDate = int(pdate_winter)
                pdate = str(year) + "/" + str(platDate).zfill(2) + "/01"
            else:
                pdate = pdateInfo['date']
            pdate_julian = pdate[2:4] + pd.Series(pd.to_datetime(pdate)).dt.dayofyear.map("{:003}".format).values[0]

            f.write("{:>2} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>29}\n"
                    .format(count, pdate_julian, "-99", "250", "250", "S", "R", "16", "0", "5", "-99", "-99", "-99",
                            "-99", "-99", "-99"))
        count = 0
        # irrigation
        f.write("\n*IRRIGATION AND WATER MANAGEMENT\n")
        for exp in data[0].keys():
            count = count + 1
            f.write("@I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME\n")
            f.write("{:>2} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:<5}\n"
                    .format(count, '-99', '-99', '-99', '-99', '-99', '-99', '-99', "-99"))
            f.write("@I IDATE  IROP IRVAL\n")
            irrigationData = data[0][exp]['irrigation'][0]
            for irrigation in irrigationData.keys():
                if irrigationData[irrigation]['simulationType'] == 'Standard' or irrigationData[irrigation][
                    'simulationType'] == 'Potential':
                    f.write("{:>2} {:>5} {:>5} {:>5}\n".format(count, '-99', '-99', '-99'))
                    break
                else:
                    irrdate = irrigationData[irrigation]["date"]
                    irrdate_julian = irrdate[2:4] + \
                                     pd.Series(pd.to_datetime(irrdate)).dt.dayofyear.map("{:003}".format).values[0]
                    f.write("{:>2} {:>5} {:>5} {:>5}\n"
                            .format(count, irrdate_julian, irrigationData[irrigation]["operation"],
                                    irrigationData[irrigation]["amount"]))
        count = 0
        # fertilizer
        f.write("\n*FERTILIZERS (INORGANIC)\n")
        f.write("@F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME\n")
        for exp in data[0].keys():
            count = count + 1
            fertilizerData = data[0][exp]['fertilizerApp'][0]
            nitr_irr = int(get_nitrogen_app_irrigated_value(dbsession, data[0][exp]['latitude'],
                 data[0][exp]['longitude']).scalar())
            nitr_rf = int(get_nitrogen_app_rainfed_value(dbsession, data[0][exp]['latitude'], #? use rainfed/irrigated
                 data[0][exp]['longitude']).scalar())
            for fertilizer in fertilizerData.keys():
                if fertilizerData[fertilizer]['simulationType'] == 'Standard' or fertilizerData[fertilizer][
                    'simulationType'] == 'Potential':
                    pdateInfo = data[0][exp]['pdate']
                    if (pdateInfo['simulationType'] == 'Standard'):
                        if (crop == 'wheat' and int(re.sub('\D', '', ME)) >= 9):
                            pdate_spring = get_plating_date_spring_wheat(dbsession, data[0][exp]['latitude'],
                                data[0][exp]['longitude']).scalar()
                            platDate = int(pdate_spring)
                        elif (crop == 'wheat' and int(re.sub('\D', '', ME)) < 9):
                            pdate_winter = get_plating_date_winter_wheat(dbsession, data[0][exp]['latitude'],
                                data[0][exp]['longitude']).scalar()
                            platDate = int(pdate_winter)
                        pdate = str(year) + "/" + str(platDate).zfill(2) + "/01"
                    else:
                        pdate = pdateInfo['date']
                    secondFertilizer = str(
                        datetime.strptime(pdate, '%Y/%m/%d').date() + timedelta(40))
                    firstFertJulian = pdate[2:4] + \
                                      pd.Series(pd.to_datetime(pdate)).dt.dayofyear.map("{:003}".format).values[0]
                    secondFertJulian = secondFertilizer[2:4] + \
                                       pd.Series(pd.to_datetime(secondFertilizer)).dt.dayofyear.map(
                                           "{:003}".format).values[0]
                    f.write("{:>2} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:<5}\n"
                            .format(count, firstFertJulian, "FE005", "AP001", "1.", nitr_irr / 2, "-99.", "-99.",
                                    "-99.", "-99.", "-99", "-99"))
                    f.write("{:>2} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:<5}\n"
                            .format(count, secondFertJulian, "FE005", "AP001", "1.", nitr_irr / 2, "-99.", "-99.",
                                    "-99.",
                                    "-99.", "-99", "-99"))
                else:
                    fertdate = fertilizerData[fertilizer]["date"]
                    fertdate_julian = fertdate[2:4] + \
                                      pd.Series(pd.to_datetime(fertdate)).dt.dayofyear.map("{:003}".format).values[0]
                    f.write("{:>2} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:<5}\n"
                            .format(count, fertdate_julian, fertilizerData[fertilizer]["source"],
                                    fertilizerData[fertilizer]["method"], "1.", fertilizerData[fertilizer]["amount"],
                                    "-99.", "-99.", "-99.", "-99.", "-99", "-99"))
        count = 0
        # tillage
        f.write("\n*TILLAGE AND ROTATIONS\n")
        f.write("@T TDATE TIMPL  TDEP TNAME\n")
        for exp in data[0].keys():
            count = count + 1
            tillageData = data[0][exp]['tillage'][0]
            for tillage in tillageData.keys():
                if tillageData[tillage]['simulationType'] == 'Standard' or tillageData[tillage][
                    'simulationType'] == 'Potential':
                    f.write("{:>2} {:>5} {:>5} {:>5} {:<5}\n".format(count, '80001', "-99", "-99",
                                                                     "-99"))  # check if date will cause trouble
                    break
                else:
                    tillagedate = tillageData[tillage]["date"]
                    tillagedate_julian = tillagedate[2:4] + \
                                         pd.Series(pd.to_datetime(tillagedate)).dt.dayofyear.map(
                                             "{:003}".format).values[0]
                    f.write("{:>2} {:>5} {:>5} {:>5} {:<5}\n"
                            .format(count, tillagedate_julian, tillageData[tillage]["type"],
                                    tillageData[tillage]["depth"], "-99"))  # check if date will cause trouble

        count = 0
        # simulation controls & automatic management
        model_id = analysis.model
        for i in range(len(analysis.model)):
            # wheat
            if model_id[i] == 'NWheat':
                model_id[i] = 'WHAPS'
            if model_id[i] == 'CERES-Wheat':
                model_id[i] = 'CSCER'
            if model_id[i] == 'CROPSIM-Wheat':
                model_id[i] = 'CSCRP'
            # maize
            # ...
            # rice
            # ...

        # make statment for each specific model
        f.write("\n*SIMULATION CONTROLS\n")
        for model in model_id:
            for exp in data[0].keys():
                count = count + 1
                pdateInfo = data[0][exp]['pdate']
                if (pdateInfo['simulationType'] == 'Standard'):
                    if (crop == 'wheat' and int(re.sub('\D', '', ME)) >= 9):
                        pdate_spring = get_plating_date_spring_wheat(dbsession, data[0][exp]['latitude'],
                                data[0][exp]['longitude']).scalar()
                        platDate = int(pdate_spring)
                    elif (crop == 'wheat' and int(re.sub('\D', '', ME)) < 9):
                        pdate_winter = get_plating_date_winter_wheat(dbsession, data[0][exp]['latitude'],
                                data[0][exp]['longitude']).scalar()
                        platDate = int(pdate_winter)
                    pdate = str(year) + "/" + str(platDate).zfill(2) + "/01"
                    startDateSim = str(datetime.strptime(pdate, '%Y/%m/%d').date() - timedelta(60))
                else:
                    pdate = pdateInfo['date']
                    startDateSim = data[0][exp]['startdate']

                sdate_julian = startDateSim[2:4] + \
                               pd.Series(pd.to_datetime(startDateSim)).dt.dayofyear.map("{:003}".format).values[0]

                # maybe change this later on to allow the user to select the number of years
                simulation_years = 2010 - int(startDateSim[0:4])

                f.write("@N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL\n")
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5} {:<25} {:<6}\n"
                        .format(count, "GE", simulation_years, "1", "S", sdate_julian, "2150",
                                "DEFAULT SIMULATION CONTR", model))

                # if for water and nitrogen stress
                irrigation_method = data[0][exp]['irrigation'][0]
                irrigation_id = list(data[0][exp]['irrigation'][0].keys())[0]

                if irrigation_method[irrigation_id][
                    'simulationType'] == 'Potential':  # if potential there will be only one occurrence
                    water_stress = "M"  # Y or M
                else:
                    water_stress = "Y"
                fertilizer_method = data[0][exp]['fertilizerApp'][0]
                fertilizer_id = list(data[0][exp]['fertilizerApp'][0].keys())[0]
                # if potential there will be only one occurrence
                if fertilizer_method[fertilizer_id]['simulationType'] == 'Potential':
                    nitro_stress = "M"  # Y or M
                else:
                    nitro_stress = "Y"
                f.write("@N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2\n")
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}\n"
                        .format(count, "OP", water_stress, nitro_stress, "N", "N", "N", "N", "N", "Y", "M"))
                f.write("@N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL\n")
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}\n"
                        .format(count, "ME", "M", "M", "E", "R", "S", "R", "R", "1", "G", "S", "2"))
                f.write("@N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS\n")
                # irrig? D? N?
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5}\n"
                        .format(count, "MA", "R", "D", "D", "R", "M"))
                f.write(
                    "@N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT\n")
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}\n"
                        .format(count, "OU", "N", "Y", "Y", "1", "Y", "Y", "Y", "Y", "Y", "N", "Y", "N", "Y"))

                f.write("\n@  AUTOMATIC MANAGEMENT\n")
                # pfist and plast
                f.write("@N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN\n")
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}\n"
                        .format(count, "PL", "80001", "80001", "40", "100", "30", "40", "10"))
                f.write("@N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF\n")
                # IMETH?
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}\n"
                        .format(count, "IR", "30", "80", "100", "GS000", "IR001", "10", "1"))
                f.write("@N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF\n")
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5} {:>5}\n"
                        .format(count, "NI", "30", "50", "25", "FE001", "GS000"))
                f.write("@N RESIDUES    RIPCN RTIME RIDEP\n")
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5}\n"
                        .format(count, "RE", "100", "1", "20"))
                f.write("@N HARVEST     HFRST HLAST HPCNP HPCNR\n")
                # HLAST?
                f.write("{:>2} {:<11} {:>5} {:>5} {:>5} {:>5}\n\n"
                        .format(count, "HA", "0", "00001", "100", "0"))


def create_cultivar_param():
    """
    Creates cultivar file for Crop Growth Simulations.
    """

def run_dssat_simulation(path, path_dssat_exe, crop, job_name):
    """
    Executes DSSAT.
    """
    os.chdir(path)

    if crop == 'wheat':
        ext = 'WHX'
    elif crop == 'rice':
        ext = 'RIX'
    elif crop == 'maize':
        ext = 'MZX'

    subprocess.call([path_dssat_exe, 'A', 'ECSM8001.'+ext])

    #put results into zip file
    output_zip_path = path + "/result.zip"
    utils.zip_dir(path, output_zip_path, job_name)

def get_simulation_predictions(job_id: int, prediction_result_file_path: str):

    """
    Creates a list of Prediction sqlalchemy objects, by parsing the input sommer result file. Prediction model is already defined in db models.
    """

