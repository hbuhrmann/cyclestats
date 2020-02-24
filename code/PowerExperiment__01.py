import sourcetocsv as cycle
import pandas as pd

####################################################################################
# TAKE ALL THE GPX,TCX and FIT source files and convert them to individual CSV files
#####################################################################################

#C:\Users\hanne\PycharmProjects\CycleStats\PowerOutputExperiments\RawInputNotProcessed
#C:\Users\hanne\PycharmProjects\CycleStats\PowerOutputExperiments\IntermediateFiles

#PC : inputpath = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/RawInputNotProcessed'
inputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RawInputNotProcessed'

#PCoutputpath = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/IntermediateFiles'

outputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/IntermediateFiles'


cycle.convertgeofilesbatch(inputpath, outputpath)

######################################################################################
# Take a list of standardised CSV files and create a single CSV file with all the data
######################################################################################
#########    THE BELOW LIST IS FOR RICHMOND ##########################################
#PCpathname = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/IntermediateFiles/'
pathname = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/IntermediateFiles/'
filelist = [
#'_gpxPowerExperiment_01_01_La_Trona.csv',
'_gpxPowerExperiment_01_02_La_Trona.csv',
'_gpxPowerExperiment_01_03_La_Trona.csv',
'_gpxPowerExperiment_01_04_La_Trona.csv',
'_gpxPowerExperiment_01_05_La_Trona.csv',
'_gpxPowerExperiment_01_06_La_Trona.csv',
'_gpxPowerExperiment_01_07_La_Trona.csv',
'_gpxPowerExperiment_01_08_La_Trona.csv'
]


cycledf = cycle.readcyclecsv(pathname,filelist)

#cycledf2 = cycle.addcomputedclimbdata(cycledf)
#cycledf[cycledf['IncludeIn2']==1].to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields.csv')
#cycledf2.to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields.csv')

cycledf3 = cycle.addcomputedclimbdata2(cycledf)
#cycledf3[cycledf3['IncludeIn2']==1].to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields2.csv')

#PCcycledf3.to_csv('C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/FinalFiles/_01_08_La_Trona.csv')

cycledf3.to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/FinalFiles/_last_7_rides.csv')
