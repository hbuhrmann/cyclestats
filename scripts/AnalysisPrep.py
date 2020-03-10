import cycleanalysis as ca
import os
from datetime import datetime as dt

####################################################################################
# TAKE THE RESULTS OF PREVIOUSLY GENERATED FINAL FILES (USING GENERALPREPREP.PY)
# AND MAKE COMPARISONS ON STUFF - THIS IS STILL A WORK IN PROGRESS
#####################################################################################

bike='enigma'

mac = 0
pc = 1

target = pc
targetfiles = 'folder'   # 'folder' or 'files'

targetdir = 'RideAnalysis/March2020/Analytics/'


targetraw = targetdir+'Raw/'
targetinter = targetdir+'Inter/'
targetfinal = targetdir+'Input/'
targetanalysis = targetdir+'Analysis/'

basedatafile = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/BaseData/basedata.xlsx',
'C:/Users/hanne/CycleData/BaseData/basedata.xlsx'
]

cycledatapath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetfinal,
'C:/Users/hanne/CycleData/'+targetfinal
]

analysisoutputpath = [
'/Users/hbuhrmann/PycharmProjects/CycleStats/'+targetanalysis,
'C:/Users/hanne/CycleData/'+targetanalysis
]

if targetfiles == 'files' :
    filelist = [
    '_fitfile1.csv',
    '_gpxfile1.csv',
    '_tcxfile1.csv',
    '_etcetera'
    ]
elif targetfiles == 'folder':
    files = os.scandir(cycledatapath[target])
    filelist = []
    for file in files:
        filename = file.name
        filelist.append(filename)

ca.readinputfiles(cycledatapath[target],analysisoutputpath[target],filelist)


