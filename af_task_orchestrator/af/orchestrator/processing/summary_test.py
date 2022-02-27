import pandas as pd
from csv import reader
import re
from datetime import datetime
import json
path_folder = '/Users/thiagoferreira53/Downloads/Embrapa-Bangladesh/Pythia+GDM/triangulo-outputs/Feb_15/-18.00S/-043.00W/'


summary_file = path_folder + 'Summary.OUT'
plantgro_file = path_folder + 'PlantGro.OUT'

import pandas as pd
df=pd.read_csv(summary_file, skiprows=3, sep=r"\s+", index_col=False, engine='python')

#funky way to get rid of @ from header
cols = df.columns[1:]
df = df.drop('EPCP', 1)
df.columns = cols

df_json = df.to_json('/Users/thiagoferreira53/Desktop/EBS_templates//1/summary_output.json', orient='records')

a = pd.read_json('/Users/thiagoferreira53/Desktop/EBS_templates//1/summary_output.json')

print(a)


##############
#plantgro

plantgro = []
last = []
trt = []
with open(plantgro_file, 'r+') as myfile:
    for myline in myfile:
        if '@YEAR' in myline:
            print(myline)
            for myline in myfile:
                trt.append(myline)
                if len(myline.strip()) == 0:
                    plantgro.append('\n'.join(trt))
                    trt = []
                    break
                last.append('\n'.join(trt))

plantgro.append(last[-1])
print(plantgro[2])
# print(YEAR, DOY)
