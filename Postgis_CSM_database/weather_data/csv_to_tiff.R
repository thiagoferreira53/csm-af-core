# Name:        csv_to_tiff
# Purpose:     Transform csv weather data from CIMMYT's HPC to tiff files
#
# Author:      Thiago Berton Ferreira, Willingthon Pavan
#              thiago.bertonf@gmail.com
# Created:     08/16/2020
# Updated:     02/07/2021 - Added pathing function

library(dplyr)
library(tidyr)
library(raster)
library(rgdal)

#setwd

#Command line only
#sourceDirectory = system("pwd", intern = T)
sourceDirectory = "/Users/thiagoferreira53/Projects/af-core/Postgis_CSM_database/weather_data"

outputDirectory = paste0(sourceDirectory,"/tiff_outputs")

#SET THE STAR
startDate = as.Date("1980/01/01",format="%Y/%m/%d")
endDate = as.Date("2010/09/30",format="%Y/%m/%d")

days<- seq(startDate, endDate, by="days")

convert_tiff<-function(day){
  DayYear<-substring(strftime(day, format = "%Y%j"),3,7)
  DOY <- gsub("(?<![0-9])0+", "", DayYear, perl = TRUE)
  
  rows <- system(paste0("cd ",sourceDirectory,"/Historical_Weather_6_Points; grep -w ",DOY," *.csv"), intern = TRUE)
  daiyValues<- gsub("[\r\n]", "", rows)
  
  splitDaily <-strsplit(daiyValues,":")
  
  fileName    <- unlist(splitDaily)[2*(1:length(daiyValues))-1]
  coordinates <- gsub("[^0-9_.-]",'',fileName)
  location <- substring(coordinates,3,nchar(coordinates)-1)
  
  fileData    <- unlist(splitDaily)[2*(1:length(daiyValues))]
  fileData <- gsub(pattern="  |   ", replacement=" ", fileData)
  fileData<-trimws(fileData, "l")
  #print(fileData)
  daily_data <- data.frame(location,fileData) %>% separate(fileData,c("DOY","SRAD","TMAX","TMIN", "RAIN","PAR", "CO2D","LRAD"),sep=" ") %>% 
    separate(location,c("LAT", "LONG"),sep="_")
  daily_data <- daily_data[,-c(3,8,9,10)]
  daily_data <- daily_data[,c(2,1,3,4,5,6)]
  
  MultiBand_raster <- rasterFromXYZ(daily_data)
  plot(MultiBand_raster)
  dateNoDash <- gsub("-","",day)
  #print(dateNoDash)
  
  if(dir.exists(file.path(outputDirectory, "/SRAD")) == FALSE)
  dir.create(file.path(outputDirectory, "/SRAD"), showWarnings = FALSE)
  writeRaster(MultiBand_raster[[1]],paste0(outputDirectory,'/SRAD/SRAD_',dateNoDash,'.tif'),overwrite=TRUE)
  
  if(dir.exists(file.path(outputDirectory, "/TMAX")) == FALSE)
  dir.create(file.path(outputDirectory, "/TMAX"), showWarnings = FALSE)
  writeRaster(MultiBand_raster[[2]],paste0(outputDirectory,'/TMAX/TMAX_',dateNoDash,'.tif'),overwrite=TRUE)
  
  if(dir.exists(file.path(outputDirectory, "/TMIN")) == FALSE)
  dir.create(file.path(outputDirectory, "/TMIN"), showWarnings = FALSE)
  writeRaster(MultiBand_raster[[3]],paste0(outputDirectory,'/TMIN/TMIN_',dateNoDash,'.tif'),overwrite=TRUE)
  
  if(dir.exists(file.path(outputDirectory, "/RAIN")) == FALSE)
  dir.create(file.path(outputDirectory, "/RAIN"), showWarnings = FALSE)
  writeRaster(MultiBand_raster[[4]],paste0(outputDirectory,'/RAIN/RAIN_',dateNoDash,'.tif'),overwrite=TRUE)
  
}

mapply(convert_tiff,days)

