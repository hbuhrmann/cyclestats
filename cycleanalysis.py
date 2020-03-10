import csv
import os
import fitparse
import pytz
import re
import xml.etree.ElementTree as et
import pandas as pd
import numpy as np
from datetime import datetime as dt

def addanydurationanalysis(outpath,filename,df,bands,bandingname,sourcecolname):

	bandcol = bandingname+'Band'
	inbanddurcol = bandingname + 'InBandDur'
	overbanddurcol = bandingname + 'OverBandDur'
	maxrundurcol = bandingname + 'MaxRunDur'

	bigdurdf = pd.DataFrame(columns=['actyear','actmonth','actyearmonth','actday','obduration', 'obandid', 'element', 'metrictype', 'oprevband', 'oband', 'onumruns'])

	pbdf = pd.DataFrame(index=bands,columns=['DataSet',bandcol,inbanddurcol,overbanddurcol,maxrundurcol])

	obname = sourcecolname+'overband'
	ibname = sourcecolname+'inband'
	prevobname = sourcecolname+'prevoverband'
	previbname = sourcecolname+'previnband'

	previ = bands[0]

	for i in bands[1:]:
		df[obname] = np.nan
		df[ibname] = np.nan
		df.loc[(df[sourcecolname] >= previ),obname] = i
		df.loc[(df[sourcecolname] >= previ) & (df[sourcecolname] <i), ibname] = i
		df[prevobname] = df[obname].shift(1)
		df[previbname] = df[ibname].shift(1)
		df['obandstart'] = ((df[prevobname] != df[obname]) | (df.activitystart == 1)) * 1
		df['obandid'] =  df.obandstart.cumsum()
		df['obduration'] = df.groupby(['obandid']).cumsum()['Duration']
		df['ibandstart'] = ((df[previbname] != df[ibname]) | (df.activitystart == 1)) * 1
		df['ibandid'] =  df.ibandstart.cumsum()
		df['ibduration'] = df.groupby(['ibandid']).cumsum()['Duration']

		pbdf.loc[i][inbanddurcol] = np.round(df[df[ibname] == i].Duration.sum(),1)
		pbdf.loc[i][overbanddurcol] = np.round(df[df[obname] == i].Duration.sum(),1)
		pbdf.loc[i][maxrundurcol] = np.round(df[df[obname] == i].obduration.max(),1)
		pbdf.loc[i].DataSet = filename[:-4]
		pbdf.loc[i][bandcol] = i

		#group and count the runs by overband and inband durations
		obrundf=pd.DataFrame(df[df[obname] == i].groupby(['actyear','actmonth','actyearmonth','actday','obandid']).obduration.max())
		obrundf.reset_index(inplace=True)

		ibrundf=pd.DataFrame(df[df[ibname] == i].groupby(['actyear','actmonth','actyearmonth','actday','ibandid']).ibduration.max())
		ibrundf.reset_index(inplace=True)

		obdurdf=pd.DataFrame(obrundf.groupby(['actyear','actmonth','actyearmonth','actday','obduration']).count())
		obdurdf.reset_index(inplace=True)
		obdurdf['element']=sourcecolname
		obdurdf['metrictype']='categoryandhigher'
		obdurdf['oprevband']=previ
		obdurdf['oband']=i
		obdurdf['onumruns']=obdurdf['obandid']

		ibdurdf=pd.DataFrame(ibrundf.groupby(['actyear','actmonth','actyearmonth','actday','ibduration']).count())
		ibdurdf.reset_index(inplace=True)
		ibdurdf['element']=sourcecolname
		ibdurdf['metrictype']='categoryonly'
		ibdurdf['iprevband']=previ
		ibdurdf['iband']=i
		ibdurdf['inumruns']=ibdurdf['ibandid']

		ibdurdf.rename(columns={'ibduration':'obduration', 'ibandid':'obandid', 'iprevband':'oprevband', 'iband':'oband', 'inumruns':'onumruns'},
			inplace=True)

		bigdurdf = bigdurdf.append(obdurdf, ignore_index=True, sort=True)
		bigdurdf=bigdurdf.append(ibdurdf,ignore_index=True,sort=True)

		previ = i

		df.drop(columns=[obname,ibname,prevobname,previbname,'obandstart','obandid','obduration','ibandstart','ibandid','ibduration'], inplace = True, axis = 1)

	return pbdf,bigdurdf

def readinputfiles(inpath,outpath,filelist):
	# inpath is a folder name
    # filelist is a list of files in the folder

	if inpath[-1:] != '/':
		inpath+='/'

	if outpath[-1:] != '/':
		outpath+='/'

	########Define the powerbands
	## Based on British Cycling and FTP (of 250W)
	## Active recovery : 0 to 55% FTP   = 0 to 137
	## Endurance : to 76%               = 138 to 190
	## Tempo : to 90%                   = 191 to 225
	## Threshold : to 105%              = 226 to 262
	## VO2Max : to 120%                 = 263 to 300
	## Anaerobic : to 150%              = 301 to 375
	## Neuromuscular : over 150%        = 376 to whatever
	## the banding condition is >= lowevalue and < upper value
	## 0 is automatically added as a start, the values in the array indicates the starting value of the band
	powerbands = [0,138,191,226,263,301,376,999]
	ftp=' (250W)'
	powerbandnames=['a Active Recovery',
	                'b Endurance',
	                'c Tempo',
	                'd Threshold',
	                'e VO2Max',
	                'f Anaerobic',
	                'g Neuromuscular',
	                'invalid']
	powerbandsubnames=['000 to 55% of FTP'+ftp,
	                   '056 to 76% of FTP'+ftp,
	                   '077 to 90% of FTP'+ftp,
	                   '091 to 105% of FTP'+ftp,
	                   '106 to 120% of FTP'+ftp,
	                   '121 to 150% of FTP'+ftp,
	                   '151% of FTP and higher'+ftp,
	                   'invalid']

	pblookup = pd.DataFrame(columns=['element','name','subname','from','to'])
	pblookup['from']=powerbands
	pblookup['to']=pblookup['from'].shift(-1)
	pblookup.loc[np.isnan(pblookup.to),'to'] = 9999
	pblookup['element'] = 'SmoothWatts3'
	pblookup['name'] = powerbandnames
	pblookup['subname'] = powerbandsubnames

	#########Define the cadence bands
	cadencebands = [0,40,50,60]
	for i in range(65,121,5):
		cadencebands.append(i)
	cadencebands.append(999)

	cdlookup = pd.DataFrame(columns=['element','name','subname','from','to'])
	cdlookup['from']=cadencebands
	cdlookup['to']=cdlookup['from'].shift(-1)
	cdlookup.loc[np.isnan(cdlookup.to),'to'] = 9999
	cdlookup['element'] = 'Cadence'
	cdlookup['name'] = cdlookup['from'].astype(int).astype(str).str.zfill(3) +' to ' + cdlookup['to'].astype(int).astype(str).str.zfill(3)+' rpm'
	cdlookup['subname'] = cdlookup['name']

	#########define the heartrate bands
	## for my measured max heart rate of 180:
	## active recovery = up to 60% = 0 to 108
	## endurance = up to 65% = 109 to 117
	## tempo = up to 75% = 118 to 135
	## lactate threshold = up to 82% = 136 to 148
	## VO2Max = up to 89% = 149 to 160
	## anearobic = up to 94% = 161 - 169
	## neuromuscular = over 94% = 170 and up
	## the banding condition is >= lowevalue and < upper value
	## 0 is automatically added as a start, the values in the array indicates the starting value of the band
	hrbands = [0,109,118,136,149,161,170,999]
	hrbandnames=['Active Recovery (to 60%)','Endurance (to 65%)','Tempo (to 75%)','Lactate Threshold (to 82%)','VO2Max (to 89%)','Anaerobic (to 94%)','Neuromuscular (over 94%)']
	maxhr=' (180bpm)'
	hrbandnames=['a Active Recovery',
	                'b Endurance',
	                'c Tempo',
	                'd Lactate Threshold',
	                'e VO2Max',
	                'f Anaerobic',
	                'g Neuromuscular',
	                'invalid']
	hrbandsubnames=['00 to 60% of max HR'+maxhr,
	                   '61 to 65% of max HR'+maxhr,
	                   '66 to 75% of max HR'+maxhr,
	                   '76 to 82% of max HR'+maxhr,
	                   '83 to 89% of max HR'+maxhr,
	                   '90 to 94% of max HR'+maxhr,
	                   'over 94% of max HR'+maxhr,
	                   'invalid']

	hblookup = pd.DataFrame(columns=['element','name','subname','from','to'])
	hblookup['from']=hrbands
	hblookup['to']=hblookup['from'].shift(-1)
	hblookup.loc[np.isnan(hblookup.to),'to'] = 9999
	hblookup['element'] = 'HeartRate'
	hblookup['name'] = hrbandnames
	hblookup['subname'] = hrbandsubnames


	#########define the speed bands
	#########equivalent mps for 10,15,20,25,30,35,40,45,50,60,70 kph
	speedbands = [0,2.78,4.17,5.56,6.94,8.33,9.72,11.11,13.89,16.67,19.44,999]
	speedbandnames = ['00 to 10kmh','11 to 15kmh','16 to 20kmh','21 to 25kmh','26 to 30kmh','31 to 35kmh','36 to 40kmh',
	                  '41 to 50kmh','51 to 60kmh','61 to 70kmh','over 70kmh','invalid']
	sblookup = pd.DataFrame(columns=['element','name','subname','from','to'])
	sblookup['from']=speedbands
	sblookup['to']=sblookup['from'].shift(-1)
	sblookup.loc[np.isnan(sblookup.to),'to'] = 9999
	sblookup['element'] = 'Speedmps'
	sblookup['name'] = speedbandnames
	sblookup['subname'] = speedbandnames


	#########define the gradient bands
	gradientbands = [-5,-0.3,-0.25,-0.20,0.25,0.3,5]
	i = -0.18
	while i < -0.11:
		gradientbands.append(round(i,2))
		i += 0.02
	while i < 0.11:
		gradientbands.append(round(i,2))
		i += 0.01
	while i < 0.21:
		gradientbands.append(round(i, 2))
		i += 0.02

	gradientbands.sort()

	grlookup = pd.DataFrame(columns=['element','name','subname','from','to'])
	grlookup['from']=gradientbands
	grlookup['to']=grlookup['from'].shift(-1)
	grlookup.loc[np.isnan(grlookup.to),'to'] = 9999
	grlookup['element'] = 'Gradient'
	grlookup['name'] = grlookup['from'].apply(lambda x: '-' + str(abs(int(x*100))).zfill(3) + ' to ' if x < 0 else '+' + str(int(x*100)).zfill(3) + ' to ') \
	                   + grlookup['to'].apply(lambda x: '-' + str(abs(int(x*100))).zfill(3) + '%' if x < 0 else '+' + str(int(x*100)).zfill(3) + '%')
	grlookup['subname'] = grlookup['name']

	#Create a big old lookup table that can be used in an "apply function" to add names and subnames to the analysis table
	bigoldlookup = pblookup.append(cdlookup,sort=False,ignore_index=True)
	bigoldlookup = bigoldlookup.append(hblookup,sort=False,ignore_index=True)
	bigoldlookup = bigoldlookup.append(grlookup,sort=False,ignore_index=True)
	bigoldlookup = bigoldlookup.append(sblookup,sort=False,ignore_index=True)

	#Create all the time categories on which reporting in excel or elsewhere will be based
	timecats = [[0,5,'a  00 - 05s'],
				[6,10,'b  06 - 10s'],
				[11,15,'c  11 - 15s'],
				[16,30,'d  16 - 30s'],
				[31,60,'e  31 - 60s'],
				[61,120,'f  01 - 02m'],
				[121,300,'g  02 - 05m'],
				[301,900,'h  05 - 15m'],
				[901,1800,'i  15 - 30m'],
				[1801,3600,'j  30 - 60m'],
				[3601,99999999,'k  60m and up']]
	tcdf = pd.DataFrame(timecats,columns=['fromsec','tosec','category'])


	#Create the container dataframe where all the power comparisons can be kept
	powercomp = pd.DataFrame(columns=['DataSet','SmoothWatts3Band','SmoothWatts3InBandDur','SmoothWatts3OverBandDur','SmoothWatts3MaxRunDur'])

	#Create the container dataframe where all the cadence comparisons can be kept
	cadencecomp = pd.DataFrame(columns=['DataSet','CadenceBand','CadenceInBandDur','CadenceOverBandDur','CadenceMaxRunDur'])

	#Create the container dataframe where all the heartrate comparisons can be kept
	hrcomp = pd.DataFrame(columns=['DataSet','HeartRateBand','HeartRateInBandDur','HeartRateOverBandDur','HeartRateMaxRunDur'])

	#Create the container dataframe where all the speed comparisons can be kept
	speedcomp = pd.DataFrame(columns=['DataSet','SpeedmpsBand','SpeedmpsInBandDur','SpeedmpsOverBandDur','SpeedmpsMaxRunDur'])

	#Create the container dataframe where all the gradient comparisons can be kept
	gradientcomp = pd.DataFrame(columns=['DataSet','GradientBand','GradientInBandDur','GradientOverBandDur','GradientMaxRunDur'])


	analyticslist = ['SmoothWatts3','Cadence','HeartRate','Speedmps','Gradient']
	#analyticslist = ['SmoothWatts3']
	bands = [powerbands,cadencebands,hrbands,speedbands,gradientbands]
	containers = [powercomp,cadencecomp,hrcomp,speedcomp,gradientcomp]
	#for now lets not be concerned with speed and gradient, these have novelty value only, i think
	#containers = [powercomp, cadencecomp, hrcomp]

	#bigdurdf = pd.DataFrame(columns=['actyear','actmonth','actday','bduration', 'bandid', 'element', 'prevband', 'band', 'numruns'])
	bigdurdf = pd.DataFrame()

	###### run through each file and create all the comparisons
	for file in filelist:
		try:
			rawdata = pd.read_csv(inpath+file)
		except Exception as e:
			print(f'{file} something went wrong {e}')
			continue

		# Add a column for previous row's activity id, so that we can use this later on
		rawdata['prevactid'] = rawdata.ActivityId.shift(1)
		rawdata['activitystart'] = (rawdata.ActivityId != rawdata.prevactid) * 1
		rawdata.drop(columns=['prevactid'])

		#Also add columns that indicates the year month and day of the activity
		rawdata['actyear'] = rawdata.Time.str.slice(start=0, stop=4)
		rawdata['actmonth'] = rawdata.Time.str.slice(start=5, stop=7)
		rawdata['actyearmonth'] = rawdata.Time.str.slice(start=0, stop=7)
		rawdata['actday'] = rawdata.Time.str.slice(start=8,stop=10)

		#print(rawdata.head())

		# create all the numeric analyses
		for i in range(0,len(analyticslist)):

			#Perform power analysis and add to the powercomp container
			element = analyticslist[i]
			print('Processing ',element,' data for ',file)
			analysisdf, durationdf = addanydurationanalysis(outpath,file, rawdata, bands[i], element, element)
			containers[i] = containers[i].append(analysisdf, ignore_index=True)
			bigdurdf = bigdurdf.append(durationdf,ignore_index=True,sort=True)

	now = dt.now()

	###### save the containers to CSV files
	'''
	for i in range(0,len(analyticslist)):

		#Write the comparison to a CSV file
		element = analyticslist[i]
		filename = element+'comps_'+ now.strftime('%Y-%m-%d %Hh%Mm%S')+'.csv'
		containers[i].to_csv(outpath + filename,index_label='Index')
		print('Saved',filename)
	'''

	# and then save bigdurdf
	#but first change some column names and the order of the columns to be more logical
	print('\n..........  start preparing final file by renaming and sorting columns ........\n')

	bigdurdf.rename(columns={'oband': 'uppervalue', 'obduration': 'runlength', 'oprevband': 'lowervalue', 'onumruns': 'numruns' },inplace=True)
	bigdurdf.drop(columns=['obandid'],inplace=True)
	columnsTitles = ['element','metrictype','actyear','actmonth','actyearmonth','actday','lowervalue','uppervalue','runlength','numruns']
	bigdurdf = bigdurdf.reindex(columns=columnsTitles)

	#Add a column with the total time spent (numruns x runlenght) so that we can later sum up the total time per time category
	#Make it a bit more readable by turning it into minutes rather than seconds
	bigdurdf['totalduration'] = bigdurdf.runlength*bigdurdf.numruns

	## and then add time buckets for each entry in durdf
	print('\n..........  add time buckets ..............................................\n')
	bigdurdf['timebucket'] = 'not assigned'
	for index,timerow in tcdf.iterrows():
		bigdurdf.loc[(bigdurdf.runlength <= timerow.tosec) & (bigdurdf.runlength >= timerow.fromsec),'timebucket'] = timerow.category

	## and also element buckets and subcategory descriptions
	print('\n..........  add element buckets ..............................................\n')
	bigdurdf['elementbucket'] = 'not assigned'
	bigdurdf['subtitle'] = 'not assigned'
	for index,lookuprow in bigoldlookup.iterrows():
		#print(lookuprow)
		bigdurdf.loc[(bigdurdf.lowervalue >= lookuprow['from']) & (bigdurdf.uppervalue <= lookuprow.to)
		             & (bigdurdf.element == lookuprow.element), ['elementbucket','subtitle']] = lookuprow['name'],lookuprow.subname

	#Make runlengths a bit more readable by transforming them to minutes
	bigdurdf['runlength'] = np.round(bigdurdf.runlength/60.0,2)
	bigdurdf['totalduration'] = np.round((bigdurdf.totalduration/60.0).astype(float),2)

	filename = 'durationcounts_' + now.strftime('%Y-%m-%d %Hh%Mm%S') + '.csv'
	bigdurdf.to_csv(outpath + filename,index_label='index')


	return