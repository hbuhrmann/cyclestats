import cycledata as cycle
import os
from datetime import datetime as dt

####################################################################################
# TAKE ALL THE GPX,TCX and FIT source files and convert them to individual CSV files
#####################################################################################
bike='enigma'

mac = 0
pc = 1

target = pc
targetfiles = 'folder'   # 'folder' or 'files'

mactargetdir = '/Users/hbuhrmann/PycharmProjects/CycleStats/bla bla bla and bla'
pctargetdir = 'C:/Users/hanne/CycleData/RideAnalysis/Dec19toFeb20/Strava'

pctargetraw = pctargetdir+'Raw/'
pctargetinter = pctargetdir+'Inter/'
pctargetfinal = pctargetdir+'Final/'

mactargetraw = mactargetdir+'Raw/'
mactargetinter = mactargetdir+'Inter/'
mactargetfinal = mactargetdir+'Final/'

#pc entries are always second and mac entries are always first
basedatafile = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/BaseData/basedata.xlsx',
'C:/Users/hanne/CycleData/BaseData/basedata.xlsx'
]

rawpath = [
mactargetraw,
pctargetraw
]

interpath = [
mactargetinter,
pctargetinter
]

outputpath = [
mactargetfinal,
pctargetfinal
]

cycle.convertgeofilesbatch(rawpath[target], interpath[target])

######################################################################################
# Take a list of standardised CSV files and create a single CSV file with all the data
######################################################################################

filelist = []

if targetfiles == 'files' :
    filelist = [
    '_fitfile1.csv',
    '_gpxfile1.csv',
    '_tcxfile1.csv',
    '_etcetera'
    ]
elif targetfiles == 'folder':
    files = os.scandir(interpath[target])
    filelist = []
    for file in files:
        filename = file.name
        prefix = filename[0:4]
        if prefix == '_gpx' or prefix == '_tcx' or prefix == '_fit':
            filelist.append(filename)


cycledf = cycle.readcyclecsv(interpath[target], filelist,basedatafile[target])

if len(cycledf) > 0 :
    cycledf2 = cycle.addcomputedclimbdata(cycledf)
    print('Writing final files ....')
    now=dt.now()
    filename='_fin_'+now.strftime('%Y-%m-%d %Hh%Mm%S')+'.csv'
    cycledf2.to_csv(outputpath[target]+filename)

    summary=cycledf2.groupby(cycledf.ActivityId)['TotalMeasuredWork','SmoothCW10'].sum()
    for index,row in summary.iterrows():
        print(index,'Measured : ',row.TotalMeasuredWork,' Calculated: ',round(row.SmoothCW10,0),' Ratio: ',round(row.TotalMeasuredWork/row.SmoothCW10,3))
else :
    print('\n-----##### NOTHING TO PROCESS #####-----\n')