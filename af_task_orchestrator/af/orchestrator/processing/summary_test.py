import pandas as pd
from csv import reader
import re
from datetime import datetime
path_folder = '/Users/thiagoferreira53/Downloads/Embrapa-Bangladesh/Pythia+GDM/triangulo-outputs/Feb_15/-18.00S/-043.00W/'
path_folder =  '/Users/thiagoferreira53/Desktop/EBS/Output_folder/c72c6ed0-7834-4401-af54-bafb7ec7c3c0/'


summary_file = path_folder + 'Summary.OUT'
plantgro_file = path_folder + 'PlantGro.OUT'
weather_file= path_folder + 'Weather.OUT'

import pandas as pd
df=pd.read_csv(summary_file, skiprows=3, sep=r"\s+", index_col=False, engine='python')

#funky way to get rid of @ from header
cols = df.columns[1:]
df = df.drop('EPCP', 1)
df.columns = cols


##############
#plantgro

df_list = []
count = 1 #for adding a new column that referes to the treatment number
with open(plantgro_file, 'r+') as myfile:
    for myline in myfile:
        if '@YEAR' in myline:
            bd = pd.DataFrame(columns = myline.split()) #get title
            for myline in myfile:
                if len(myline.strip()) == 0: #skip to the next if there is no more row for the treatment
                    break
                bd.loc[len(bd)] = myline.split() #append rows to the dataframe
            bd['TRT'] = count
            count = count + 1
            df_list.append(bd)

#print(df_list)
df = pd.concat(df_list)
print(df)