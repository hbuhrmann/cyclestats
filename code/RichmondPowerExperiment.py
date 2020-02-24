import sourcetocsv as cycle
import pandas as pd

####################################################################################
# TAKE ALL THE GPX,TCX and FIT source files and convert them to individual CSV files
#####################################################################################

#C:\Users\hanne\PycharmProjects\CycleStats\PowerOutputExperiments\RawInputNotProcessed
#C:\Users\hanne\PycharmProjects\CycleStats\PowerOutputExperiments\IntermediateFiles

#PC :
inputpath = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondRaw'
#mac inputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RawInputNotProcessed'

#PC
outputpath = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondInter'

#mac outputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondInter'


cycle.convertgeofilesbatch(inputpath, outputpath)

######################################################################################
# Take a list of standardised CSV files and create a single CSV file with all the data
######################################################################################
#########    THE BELOW LIST IS FOR RICHMOND ##########################################
#pc
pathname = 'C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondInter/'
#mac pathname = '/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondInter/'
filelist = [
'_gpx_20Jan2020.csv',
'_fit71329966.csv',
'_fit155981351.csv',
'_fit222172491.csv',
'_fit2998662524.csv',
'_fit3011260366.csv',
'_fit274359271.csv',
'_fit417875520.csv',
'_fit93303763.csv'
]


cycledf = cycle.readcyclecsv(pathname,filelist)


cycledf2,cycledf3 = cycle.addcomputedclimbdata(cycledf)
#pc
cycledf2.to_csv('C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondFinal/_full_dataset.csv')
#max cycledf2.to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondFinal/_full_dataset.csv')


#cycledf3 = cycle.addcomputedclimbdata2(cycledf)
#cycledf3[cycledf3['Inc ludeIn2']==1].to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields2.csv')

#PC
cycledf3.to_csv('C:/Users/hanne/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondFinal/_reduced_dataset.csv')

#mac cycledf3.to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/PowerOutputExperiments/RichmondFinal/_all_test_files.csv')
