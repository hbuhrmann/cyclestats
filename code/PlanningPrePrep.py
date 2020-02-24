import cycledata as cycle
import os
from datetime import datetime as dt


mac = 0
pc = 1


target = pc
targetfiles = 'folder'   # 'folder' or 'files'


targetdir = 'PlanningExperiments/Gen'

targetraw = targetdir+'Raw/'
targetinter = targetdir+'Inter/'
targetfinal = targetdir+'Final/'

basedatafile = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/BaseData/basedata.xlsx',
'C:/Users/hanne/CycleData/BaseData/basedata.xlsx'
]

rawpath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetraw,
'C:/Users/hanne/CycleData/'+targetraw
]

interpath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetinter,
'C:/Users/hanne/CycleData/'+targetinter
]

outputpath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetfinal,
'C:/Users/hanne/CycleData/'+targetfinal
]

cycle.convertroutefilesbatch(rawpath[target], interpath[target])

######################################################################################
# Take a list of standardised CSV files and create a single CSV file with all the data
######################################################################################

filelist = []

if targetfiles == 'files' :
    filelist = [ '_planfile1.csv','_etcetera' ]
elif targetfiles == 'folder':
    files = os.scandir(interpath[target])
    filelist = []
    for file in files:
        filename = file.name
        prefix = filename[0:4]
        if prefix == '_gpx' or prefix == '_tcx' or prefix == '_fit':
            filelist.append(filename)


cycle.createroutetargetsfromavgwatts(interpath[target], filelist,outputpath[target],basedatafile[target])

#print('Writing final files ....')
#now=dt.now()
#filename=bike+'_plan '+now.strftime('%Y-%m-%d %Hh%Mm%S')+'.csv'
#plandf.to_csv(outputpath[target]+filename)
