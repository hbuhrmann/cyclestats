import sourcetocsv as cycle
import os
from datetime import datetime as dt


####################################################################################
# TAKE ALL THE GPX route files and convert them to CSV files
#####################################################################################

riderweight=75
bikeweight=10
crr=0.0025
rho=1.25

targetwatts = 200

#----SET THE WIND SPEED AND DIRECTION
#    0 degrees = blowing TO the north, 180 degrees = blowing to the south, 90 degrees = blowing to the east, 270 degrees = blowing to the west
#    Windspeed in kilometres per hour
#    For the time being there seems to be an exaggeration in power calculation if you use the provided windspeed
#    It seems that if you use 0.3125 x real windspeed, you get a better approximation of real world power
#    The other problem, which has not yet been addressed, is that the windspeed is applied to all the files, regardless of when and where the
#    actual ride took place. In reality, there should be some kind of wind lookup file

wspeedkph = 0
wdirdeg = 0
fhw = 0.31125
ftw = 0.46125

#----CHOOSE THE RIGHT BIKE
bike='enigma'

if bike == 'wahoo':
    # this is an indoor trainer - there is no wind.....
    wspeedkph = 0
    wdirdeg = 0
    cd=0.535
    fa=0.5
    exfact = 1.5
elif bike == 'enigma':
    cd=0.7
    fa=0.55
    exfact=1.25
else: #This should never happen, but if it does then the power curves would just be weird
    cd=0.01
    fa=0.01
    exfact=1

mac = 0
pc = 1


target = pc
targetfiles = 'folder'   # 'folder' or 'files'


targetdir = 'PlanningExperiments/Gen'

targetraw = targetdir+'Raw/'
targetinter = targetdir+'Inter/'
targetfinal = targetdir+'Final/'

rawpath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetraw,
'C:/Users/hanne/PycharmProjects/CycleStats/'+targetraw
]

interpath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetinter,
'C:/Users/hanne/PycharmProjects/CycleStats/'+targetinter
]

outputpath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetfinal,
'C:/Users/hanne/PycharmProjects/CycleStats/'+targetfinal
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

cycle.createroutetargetsfromavgwatts(interpath[target], filelist,outputpath[target],riderweight, bikeweight, crr, rho, cd, fa, exfact, wspeedkph,wdirdeg,fhw,ftw,targetwatts)

#print('Writing final files ....')
#now=dt.now()
#filename=bike+'_plan '+now.strftime('%Y-%m-%d %Hh%Mm%S')+'.csv'
#plandf.to_csv(outputpath[target]+filename)
