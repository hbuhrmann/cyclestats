import sourcetocsv as cycle
import pandas as pd

####################################################################################
# TAKE ALL THE GPX,TCX and FIT source files and convert them to individual CSV files
#####################################################################################

#PC :
inputpath = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/StagesRaw'
#mac inputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RawInputNotProcessed'

#PC
outputpath = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/StagesInter'

#mac outputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondInter'


cycle.convertgeofilesbatch(inputpath, outputpath)

######################################################################################
# Take a list of standardised CSV files and create a single CSV file with all the data
######################################################################################
#########    THE BELOW LIST IS FOR RICHMOND ##########################################
#pc
pathname = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/StagesInter/'
#mac pathname = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondInter/'
filelist = [
'_fit2020-01-26-09-23-40.csv'
#'_gpxHeartrate_Data_Exercise_Kinomap_Venice_Beach 01.csv',
#'_gpxHeartrate_Data_Exercise_Kinomap_Venice_Beach 02.csv'
]


cycledf = cycle.readcyclecsv(pathname,filelist,riderweight=75, bikeweight=10, crr=0.0025, rho=1.25, cd=0.75, fa=0.6)

cycledf2,cycledf3 = cycle.addcomputedclimbdata(cycledf)
#pc
cycledf2.to_csv('C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/StagesFinal/_full_dataset.csv')
#max cycledf2.to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondFinal/_full_dataset.csv')


#cycledf3 = cycle.addcomputedclimbdata2(cycledf)
#cycledf3[cycledf3['Inc ludeIn2']==1].to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields2.csv')

#PC
cycledf3.to_csv('C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/StagesFinal/_reduced_dataset.csv')

#mac cycledf3.to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondFinal/_all_test_files.csv')
