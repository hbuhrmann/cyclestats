import sourcetocsv as cycle
import pandas as pd

####################################################################################
# TAKE ALL THE GPX,TCX and FIT source files and convert them to individual CSV files
#####################################################################################

inputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/TestData'
outputpath = '/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep1'

#cycle.convertgeofilesbatch(inputpath, outputpath)

######################################################################################
# Take a list of standardised CSV files and create a single CSV file with all the data
######################################################################################
#########    THE BELOW LIST IS FOR RICHMOND ##########################################
pathname = '/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep1/'
filelist = [
'_tcx2434361860.csv',
'_tcx2312822501.csv',
'_gpx2159398600.csv',
'_fit41902412.csv',
'_tcx2278974971.csv',
'_tcx2347388740.csv',
'_gpx196305244.csv',
'_gpx2161805621.csv',
'_fit2398259521.csv',
'_fit207905658.csv',
'_fit41902327.csv',
'_fit66161015.csv',
'_fit41902393.csv',
'_fit316436609.csv',
'_fit51827795.csv',
'_tcx2247411918.csv'
]


cycledf = cycle.readcyclecsv(pathname,filelist)

#cycledf2 = cycle.addcomputedclimbdata(cycledf)
#cycledf[cycledf['IncludeIn2']==1].to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields.csv')
#cycledf2.to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields.csv')

cycledf3 = cycle.addcomputedclimbdata2(cycledf)
cycledf3[cycledf3['IncludeIn2']==1].to_csv('/Users/hbuhrmann/PycharmProjects/CycleStats/TestStep2/extendedfields2.csv')

