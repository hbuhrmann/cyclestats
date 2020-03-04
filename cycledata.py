import csv
import os
import fitparse
import pytz
import re
import xml.etree.ElementTree as et
import pandas as pd
import numpy as np
import datetime


# takes in a GPX file of an actual ride and outputs a CSV file
# Must have at least latitude, longitude, altitude and time
def convertrideGPX(input,output,fileid):

    error = False
    errorcount = 0
    lasterror = ''
    lines = 0

    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r'^({.*})', root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ''

    if root.tag != ns + 'gpx':
        print('Looking for root "gpx", but Unknown root found: ' + root.tag)
        return lines, error, errorcount, lasterror

    metadata = root.find(ns+ 'metadata')
    if not metadata:
        print('Unable to find "gpx.metadata"')
        return lines,error,errorcount,lasterror
    '''
    try:
        id = metadata.find(ns + 'time').text.strip()
        stripped = id.replace('T', ' ')
        stripped = stripped.replace('Z', '')
        actid = '_' + input[0:-4]  #''.join(stripped)
    except:
        actid = ''
    '''
    actid = fileid
    tracks = root.find(ns + 'trk')
    if not tracks:
        print('Unable to find "trk" under root')
        return lines, error, errorcount, lasterror

    columnsEstablished = False

    tracksegments = tracks.find(ns + 'trkseg')
    if not tracksegments:
        print('Unable to find "trkseg" under "trk"')
        return lines, error, errorcount, lasterror

    if columnsEstablished:
        fout.write('New Track Segment\n')

    for trackpoint in tracksegments.iter(ns + 'trkpt'):

        #print (trackpoint.get('lat'))

        lines += 1
        rowid = "{:0>7d}".format(lines)
        lasterror = ''

        time = ''
        latitude = ''
        longitude = ''
        distance = ''
        altitude=''
        bpm=''
        cadence=''
        watts=''
        speed = ''
        try:
            time = trackpoint.find(ns + 'time').text.strip()
            time = time.replace('T', ' ')
            time = time.replace('Z', '')
        except:
            time = ''
            error = True
            errorcount += 1
            lasterror += 'time |'
        try:
            latitude = trackpoint.get('lat').strip()
        except:
            latitude = ''
            error = True
            errorcount += 1
            lasterror += 'latitude |'
        try:
            longitude = trackpoint.get('lon').strip()
        except:
            longitude = ''
            error = True
            errorcount += 1
            lasterror += 'longitude |'
        try:
            altitude = trackpoint.find(ns + 'ele').text.strip()
        except:
            altitude = ''
            error = True
            errorcount += 1
            lasterror += 'altitude |'

        #gpx files does not contain a distance field or a speed field
        speed = ''
        distance = ''

        for extension in trackpoint.iter(ns + 'extensions'):
            try:
                watts = extension.find(ns+'power').text.strip()
            except:
                watts = ''
                error = True
                errorcount += 1
                lasterror += 'watts |'

            bpm = ''
            cadence = ''

            for tpextension in extension.iter():
                if tpextension.tag[-2:] == 'hr':
                    bpm = tpextension.text.strip()
                elif tpextension.tag[-3:] == 'cad':
                    cadence = tpextension.text.strip()

        if not columnsEstablished:
            filetype = 'gpx'
            fout = open(output, 'w')
            fout.write(','.join(
                ('FileType','RowId', 'ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'DistanceMeters',
                 'AltitudeMeters', 'HeartRate', 'Cadence', 'Watts', 'Speed')) + '\n')
            columnsEstablished = True
        fout.write(
            ','.join((filetype,rowid, actid, time, latitude, longitude, distance, altitude, bpm, cadence, watts, speed)) + '\n')

    return lines, error, errorcount, lasterror


# Some of the Garmin TCX files puts whitespace at the start of the file. this function removes the whitespace
def prepTCXfile(inputfolder, inputfile, outputfolder, outputfile):
    file = open(inputfolder + '/' + inputfile, 'r')
    fulltext = file.readlines()
    file.close()

    if fulltext[0][0] == ' ':

        while fulltext[0][0] == ' ':
            fulltext[0] = fulltext[0][1:]

        outfile = open(inputfolder + '/' + inputfile, 'w')
        outfile.writelines(fulltext)

        outfile.close()

    return


# takes in a TCX file and outputs a CSV file
# Must have at least longitude, latitude, altitude and time
def convertrideTCX(input,output,fileid):
    error = False
    errorcount = 0
    lasterror = ''
    lines = 0
    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r'^({.*})', root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ''
    if root.tag != ns + 'TrainingCenterDatabase':
        print('Unknown root found: ' + root.tag)
        return
    activities = root.find(ns + 'Activities')
    if not activities:
        activities = root.find(ns + 'Courses')
        if not activities:
            print('Unable to find Activities or Courses under root')
            return
    activity = activities.find(ns + 'Activity')
    if not activity:
        activity = activities.find(ns + 'Course')
        if not activity:
            print('Unable to find Activity or Course under Activities/Courses')
            return
    actid = fileid
    columnsEstablished = False
    for lap in activity.iter(ns + 'Lap'):
        if columnsEstablished:
            fout.write('New Lap\n')
        for track in lap.iter(ns + 'Track'):
            # pdb.set_trace()
            if columnsEstablished:
                fout.write('New Track\n')
            for trackpoint in track.iter(ns + 'Trackpoint'):
                lines += 1
                excludeline = False
                rowid="{:0>7d}".format(lines)
                lasterror = ''
                try:
                    time = trackpoint.find(ns + 'Time').text.strip()
                    time = time.replace('T', ' ')
                    time = time.replace('Z', '')
                except:
                    time = ''
                    error = True
                    errorcount += 1
                    lasterror += 'time |'
                    excludeline = True
                try:
                    latitude = trackpoint.find(ns + 'Position').find(ns + 'LatitudeDegrees').text.strip()
                except:
                    latitude = ''
                    error = True
                    errorcount += 1
                    lasterror += 'latitude |'
                    excludeline = True;
                try:
                    longitude = trackpoint.find(ns + 'Position').find(ns + 'LongitudeDegrees').text.strip()
                except:
                    longitude = ''
                    error = True
                    errorcount += 1
                    lasterror += 'longitude |'
                    excludeline = True
                try:
                    altitude = trackpoint.find(ns + 'AltitudeMeters').text.strip()
                except:
                    altitude = ''
                    error = True
                    errorcount += 1
                    lasterror += 'altitude |'
                    excludeline = True
                try:
                    distance = trackpoint.find(ns + 'DistanceMeters').text.strip()
                except:
                    distance = ''
                    error = True
                    errorcount += 1
                    lasterror += 'distance |'
                try:
                    bpm = trackpoint.find(ns + 'HeartRateBpm').find(ns + 'Value').text.strip()
                except:
                    bpm = ''
                    error = True
                    errorcount += 1
                    lasterror += 'heart |'
                try:
                    cadence = trackpoint.find(ns + 'Cadence').text.strip()
                except:
                    cadence = ''
                    error = True
                    errorcount += 1
                    lasterror += 'cadence |'
                try:
                    watts = ''
                    speed = ''
                    # watts=trackpoint.find(ns+'Extensions').text.strip()
                    for extension in trackpoint.iter(ns + 'Extensions'):
                        for extension2 in extension.iter():
                            if extension2.tag[-5:] == 'Watts':
                                watts = extension2.text.strip()
                            if extension2.tag[-5:] == 'Speed':
                                speed = extension2.text.strip()
                except:
                    watts = ''
                    speed = ''
                    error = True
                    errorcount += 1
                    lasterror += 'speedorpower |'

                if not columnsEstablished:
                    filetype='tcx'
                    fout = open(output, 'w')
                    fout.write(','.join(('FileType','RowId','ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'DistanceMeters',
                                         'AltitudeMeters', 'HeartRate', 'Cadence', 'Watts', 'Speed')) + '\n')
                    columnsEstablished = True

                if excludeline != True:
                    fout.write(
                        ','.join((filetype,rowid, actid, time, latitude, longitude, distance, altitude, bpm, cadence, watts, speed)) + '\n')

    fout.close()
    return lines, error, errorcount, lasterror

# takes in a FIT file and outputs a CSV file
# must have at least latitude, longitude, altitude and time
def convertrideFIT(fitfile, output_file, fileid):

    # Prepare all the mapping naming conventions and mandaotry elements
    # The following fields appear to available on Garmin FIT files with a Stages Power Meter
    # position_lat position_long  distance  accumulated_power  enhanced_altitude  altitude  enhanced_speed  speed  power
    # heart_rate  cadence  temperature  left_torque_effectiveness  right_torque_effectiveness  left_pedal_smoothness  right_pedal_smoothness

    allowed_fields = ['file_type','row_id', 'activity_id', 'timestamp', 'position_lat', 'position_long', 'distance', 'altitude',
                      'speed', 'heart_rate', 'cadence', 'power','temperature']
    mapped_names = ['FileType','RowId', 'ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'DistanceMeters',
                    'AltitudeMeters', 'Speed', 'HeartRate', 'Cadence', 'Watts','Temperature']

    required_fields = ['FileType','RowId', 'ActivityId', 'Time', 'LatitudeDegrees', 'LongitudeDegrees', 'AltitudeMeters']

    UTC = pytz.UTC

    linecount = 1
    messages = fitfile.messages
    data = []
    for m in messages:
        skip = False
        if not hasattr(m, 'fields'):
            continue
        fields = m.fields

        # add an activity identity column
        # check for important data types
        mdata = {}
        for field in fields:
            if field.name in allowed_fields:
                fieldname = mapped_names[allowed_fields.index(field.name)]
                if field.name == 'timestamp':
                    timestamp=field.value.strftime('%Y/%m/%d %H:%M:%S')
                    mdata[fieldname] = timestamp
                    mdata['RowId'] = linecount
                    mdata['ActivityId'] =  fileid
                    mdata['FileType'] = 'fit'
                else:
                    #First remove some horribleness with cadence, watts and heartrate, where it is sometimes set to a non-numeric
                    if fieldname == 'Cadence' or fieldname == 'HeartRate':
                        try:
                            fieldval = float(field.value)
                        except:
                            fieldval = np.nan
                        mdata[fieldname] = fieldval
                    else:
                        mdata[fieldname] = field.value
        for rf in required_fields:
            if rf not in mdata:
                skip = True
        if not skip:
            linecount+=1
            data.append(mdata)
    # write to csv
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(mapped_names)
        for entry in data:
            writer.writerow([str(entry.get(k, '')) for k in mapped_names])

    return linecount


# Takes an inputfolder and converts all the GPX,FIT and TCX files in the folder to a uniform CSV format
def convertgeofilesbatch(inputpath, outputpath):
    files = os.scandir(inputpath)
    countTcx = 0
    countFit = 0
    countGpx = 0
    results = []
    results.append(['Filename','Outputfile','Linecount','Errorfound','Errorcount','Errortext'])
    for file in files:
        inputfilename = file.name
        fileid = '_' + inputfilename[:-4]
        if file.name[-3:].upper() == 'FIT':
            outputfilename = '_fit' + inputfilename[:-3]+'csv'
            cvinput = inputpath + inputfilename
            cvoutput = outputpath + outputfilename
            print('FIT : ',cvinput,'    -     ',cvoutput)
            fitfile = fitparse.FitFile(cvinput, data_processor=fitparse.StandardUnitsDataProcessor())
            lines = convertrideFIT(fitfile, cvoutput,fileid)
            results.append([file.name,outputfilename,lines,'','',''])
        elif file.name[-3:].upper() == 'TCX':
            outputfilename = '/_tcx' + ''.join(file.name)
            countTcx += 1
            prepTCXfile(inputpath, file.name, outputpath, outputfilename)
            cvinput = inputpath + inputfilename
            cvoutput = outputpath + outputfilename[0:-3] + 'csv'
            print('TCX : ',cvinput,'    -     ',cvoutput)
            lines, error, errorcount, lasterror = convertrideTCX(cvinput, cvoutput,fileid)
            results.append([file.name,outputfilename[1:-3] + 'csv', lines, error, errorcount, lasterror])
        elif file.name[-3:].upper() == 'GPX':
            outputfilename = '/_gpx' + ''.join(file.name)
            countGpx += 1
            cvinput = inputpath + inputfilename
            cvoutput = outputpath + outputfilename[0:-3] + 'csv'
            print('GPX : ',cvinput,'    -     ',cvoutput)
            lines, error, errorcount, lasterror = convertrideGPX(cvinput, cvoutput,fileid)
            results.append([file.name,outputfilename[1:-3] + 'csv', lines, error, errorcount, lasterror])

        with open(outputpath+'/'+'___process_report.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for line in results:
                writer.writerow(line[i] for i in range(0,len(line)))
        f.close()


# Takes a dataframe and adds geographic distance columns to the dataframe
def addgeodistanceindf(df,curlatname,prevlatname,curlongname,prevlongname,curaltname,prevaltname,distxycolname,distxyzcolname):

    earthradius =   6371000  # meter
    latdiff = np.radians(df[curlatname]) - np.radians(df[prevlatname])
    longdiff = np.radians(df[curlongname]) - np.radians(df[prevlongname])
    lat1rad = np.radians(df[curlatname])
    lat2rad = np.radians(df[prevlatname])
    altdiff = df[curaltname]-df[prevaltname]

    a = np.sin(latdiff/2.0)**2 + np.cos(lat1rad)*np.cos(lat2rad)*np.sin(longdiff/2.0)**2
    c = 2*np.arctan2(np.sqrt(a),np.sqrt(1-a))
    d = np.round(earthradius*c,2) # distance in the xy plane
    d3 = np.round(np.sqrt(d*d+altdiff*altdiff),2) #distance in the 3 dimensional plane

    df[distxycolname] = d
    df[distxyzcolname] = d3

    return df

# Calculates power data from gradient, entry speed into the datapoint, and acceleration acceleration over the datapoint
def addcalculatedpowerdata(sourcedf,riderweight,bikeweight,crr,rho,cd,fa):

    #Please not that the calculated power may be negative, (mostly on descents, but also under deceleration

    powertemp = 3.5

    g = 9.8067 #Gravity
    weight = riderweight+bikeweight

    sourcedf['FGravity10'] = np.round(g * np.sin(np.arctan(sourcedf.SmoothGradient10)) * weight * sourcedf.SmoothSpeed10 * sourcedf.Duration ,2)
    sourcedf['FRolling10'] = np.round(g * np.cos(np.arctan(sourcedf.SmoothGradient10)) * weight * crr * sourcedf.SmoothSpeed10 * sourcedf.Duration ,2)
    sourcedf['FDrag10'] = np.round(0.5 * cd * fa * rho * (sourcedf.SmoothSpeed10 - sourcedf.Relwspeed10)**2 * sourcedf.SmoothSpeed10 * sourcedf.Duration,2)
    sourcedf['FAccel10'] = np.round((sourcedf.SmoothSpeed10 - sourcedf.SmoothSpeed10.shift(periods=1)) * weight,2)
    sourcedf['CalculatedWork10'] = np.round((sourcedf.FGravity10 + sourcedf.FRolling10 + sourcedf.FDrag10 + sourcedf.FAccel10),2)
    sourcedf['CalculatedPower10'] = np.round(sourcedf.CalculatedWork10 / (sourcedf.Duration ),2)

    return sourcedf


#The calculated power is quite peaky - reduce the peakiness
def reduceoutliers(df, colname, adjcolname, xfact=1.25, minval=np.nan, maxval=np.nan):
    '''
    Smoothing of calculated power curves. Calculatedpower curvers on historic cycle data is seriously peaky
    We are basically trying to reduce the standard deviation, and reign in the extreme outliers exponentially more than the datapoints close to the mean
    This method works ok if power exertion over the duration of the ride is quite consistent, but if you do interval training it may go a bit bad

    The current calculated power curve contains both positive and negative values (which is theoretically accurate)
    The smoothing will be applied on the true values of the calculated set, and all negative smoothed values will then be removed

    Algorithm :

    1. Calculate the mean calculated power "cpmean"
    2. Calculate the distance between the "cpmean" and the datapoint : "distancetomean"
    3. Reduce this distance by a expfactor "xf" i.e. "distancemean"**(1/"xf"), where "xf" > 1 (1.25 seems to work nice)
       If "xf" < 1 you can use the same principle to exponentially exaggerate the outliers

    4. Full formula : math.copysign((ABS(cpmean-datapoint))**xfactor,datapoint-cpmean)+cpmean
    in excel : (ABS(cpmean-datapoint))^(1/1.25)*SIGN(datapoint-cpmean)+cpmean
    '''

    # df is a dataframe containing a column whose values need to be adjusted
    # colname is the name of the column containing the datapoints
    # xfact is the factor by which the values need to be adapted

    # the function will return the dataframe with an additionalcolumn adjcolname

    mean = df[colname].mean()

    df[adjcolname] = np.round((abs(mean - df[colname])) ** (1 / xfact) * np.sign(df[colname] - mean) + mean,2)

    if np.isnan(minval) != True:
        df[adjcolname] = df[adjcolname].apply(lambda x: 0 if x < minval else x)

    if np.isnan(maxval) != True:
        df[adjcolname] = df[adjcolname].apply(lambda x: 0 if x > maxval else x)

        return df

# Calculates power data
def smoothcalculatedpowerdata(sourcedf,originalpowercolumn,smoothedpowercolumn,smoothedworkcolumn,durationcolumn,exfact=1.25):

    miv = np.nan   #minval
    mav = np.nan   #maxval

    #For the full dataset
    reduceoutliers(sourcedf, originalpowercolumn, smoothedpowercolumn, exfact, minval=miv, maxval=mav)
    sourcedf[smoothedworkcolumn] = sourcedf[smoothedpowercolumn] * sourcedf[durationcolumn]

    return sourcedf

# Takes the raw cycle data and add a few computed columns : xy distance, xyz distance, speed, gradient, elapsed time
# between points and so forth
def addcomputedcycledata(sourcedf,riderweight, bikeweight, crr, rho, cd, fa, exfact,wspeedkph,wdirdeg,fhw,ftw):

    #First add columns that may be missing
    #For now it is only Watts that seems to be missing but in future there may be more
    if 'Watts' not in sourcedf.columns:
        sourcedf['Watts'] = np.nan

    sourcedf[['PrevLat','PrevLong','PrevAlt','PrevTime']] = sourcedf[['LatitudeDegrees','LongitudeDegrees','AltitudeMeters','Time']].shift(periods=1)
    #Calculate all the geo distances

    addgeodistanceindf(sourcedf, curlatname = 'LatitudeDegrees', prevlatname = 'PrevLat', curlongname = 'LongitudeDegrees',
                       prevlongname = 'PrevLong', curaltname = 'AltitudeMeters', prevaltname = 'PrevAlt',
                       distxycolname = 'DistXY', distxyzcolname = 'DistXYZ')

    '''
    #Drop all rows where the xy distance = 0 (they are spurious and interfere with the smoothing calculations)
    sourcedf['nextdistxy']=sourcedf.DistXY.shift(-1)
    rowstodrop = sourcedf[(sourcedf.DistXY == 0) & (sourcedf.nextdistxy == 0)].index
    sourcedf.drop(rowstodrop,inplace=True)
    sourcedf.drop(columns=['nextdistxy'],inplace=True,axis=1)

    #Recalculate all the geo distances
    addgeodistanceindf(sourcedf, curlatname = 'LatitudeDegrees', prevlatname = 'PrevLat', curlongname = 'LongitudeDegrees',
                       prevlongname = 'PrevLong', curaltname = 'AltitudeMeters', prevaltname = 'PrevAlt',
                       distxycolname = 'DistXY', distxyzcolname = 'DistXYZ')
    '''
    sourcedf[['PrevLat','PrevLong','PrevAlt','PrevTime']] = sourcedf[['LatitudeDegrees','LongitudeDegrees','AltitudeMeters','Time']].shift(periods=1)

    sourcedf['CumDistXYZ'] = sourcedf.DistXYZ.cumsum()
    sourcedf['Elevation'] = sourcedf['AltitudeMeters'].astype(float)-sourcedf['PrevAlt'].astype(float)
    sourcedf['Direction'] = np.degrees(np.arctan2((sourcedf['LongitudeDegrees'] - sourcedf['PrevLong']),
                                                  (sourcedf['LatitudeDegrees'] - sourcedf['PrevLat']))).apply(lambda x: x if x >= 0 else 360 + x)
    sourcedf['Direction'] = np.round(sourcedf.Direction,0)
    sourcedf['Gradient'] = (sourcedf['Elevation']/sourcedf['DistXY']).apply(lambda x: 0 if x == np.inf else 0 if x == -np.inf else x)
    sourcedf['Gradient'] = np.round(sourcedf.Gradient,3)
    #Make sure that all gradients are set to a number (set to 0 if not a number)
    sourcedf['Gradient']=sourcedf['Gradient'].apply(lambda x: 0 if np.isnan(x) == True else x)

    time = pd.to_datetime(sourcedf['Time']).astype(np.int64)
    prevtime = pd.to_datetime(sourcedf['PrevTime']).astype(np.int64)

    prevtime[0]=time[0]
    starttime = time[0]
    sourcedf['Duration']=(time-prevtime)/1000000000.0
    sourcedf['ElapsedDuration']=(time-starttime)/1000000000.0

    sourcedf['Speedmps']=np.round(sourcedf['DistXYZ'].astype(np.float)/sourcedf['Duration'].astype(np.float),3)
    #Determine the rows that indicate the bike was stationary
    #This is a bit of a hack that seems to work for Garmin
    #It appears that any row where the duration is more than 1 second is a stationary row, but not quite
    #I added the condition that the speed must be below 0.2mps just as an extra safety -

    #Add some stuff that will be very useful to show on map layers in QGIS
    sourcedf['StationaryDuration']=sourcedf.Duration
    sourcedf.loc[(sourcedf.Duration < 2) | ((sourcedf.Duration >= 2) & (sourcedf.Speedmps > 0.2)),'StationaryDuration']=0
    sourcedf['CumStatDuration'] = sourcedf.StationaryDuration.cumsum()
    sourcedf['CumMoveDuration'] = sourcedf.ElapsedDuration-sourcedf.CumStatDuration

    sourcedf['TotalMeasuredWork']=sourcedf.Watts*sourcedf.Duration
    sourcedf['CumMeasuredWork']=sourcedf.TotalMeasuredWork.cumsum()
    sourcedf['AvCumPower']=np.round(sourcedf.CumMeasuredWork/sourcedf.CumMoveDuration,1)
    sourcedf['AvMoveSpeedkph']=np.round(sourcedf.CumDistXYZ/sourcedf.CumMoveDuration*3.6,1)
    sourcedf['AvOverallSpeedkph']=np.round(sourcedf.CumDistXYZ/sourcedf.ElapsedDuration*3.6,1)

    timeh = np.floor(sourcedf.ElapsedDuration / 3600)
    timemin = np.floor((sourcedf.ElapsedDuration - timeh * 3600) / 60)
    timehstr = timeh.apply(lambda x: '{:02d}'.format(int(x)))
    timeminstr = timemin.apply(lambda x: '{:02d}'.format(int(x)))
    timestring = timehstr + ':' + timeminstr
    diststring = sourcedf.CumDistXYZ.apply(lambda x: str(round(x / 1000, 1)) + 'km')
    stoplabel = sourcedf.StationaryDuration.apply(lambda x: '  {:2d}m'.format(int(x / 60)) + '{:02d}s'.format(int(x) - int(x / 60) * 60) + ' stop' if x > 1 else '')
    gpslabel = timestring + '  -  ' + diststring + stoplabel
    sourcedf['gpslabel']=gpslabel
    sourcedf['showgpslabel']=sourcedf.ElapsedDuration.apply(lambda x: 1 if int(x/300) == int(x)/300 else 0)
    sourcedf['showstoplabel']=sourcedf.StationaryDuration.apply(lambda x: 1 if x > 1 else 0)
    sourcedf.loc[(sourcedf.showgpslabel==0) & (sourcedf.showstoplabel == 0),'gpslabel'] = ''
    sourcedf.drop(columns=['showgpslabel','showstoplabel'],inplace=True,axis=1)
    #End of QGIS stuff

    wspeedmps = round(wspeedkph/3.6,3)
    sourcedf['Windspeedmps'] = wspeedmps
    sourcedf['Winddirection'] = wdirdeg
    sourcedf['Relwspeedmps']=np.round((np.cos(np.radians(sourcedf['Direction']-sourcedf['Winddirection']))*sourcedf['Windspeedmps']),3)


    #The altitude data is particularly spiky - the below will smooth altitude and gradient
    sourcedf['SumDistance10']=sourcedf.DistXYZ.rolling(window=10,min_periods=1).sum()
    sourcedf['SumDuration10'] = sourcedf.Duration.rolling(window=10,min_periods=1).sum()
    sourcedf['smoothalt']=np.round(sourcedf.AltitudeMeters.rolling(window=10,min_periods = 1).mean()*5,0)/5
    sourcedf['SmoothAltitude10']=sourcedf.smoothalt.shift(-5)
    sourcedf['SmoothElevation10']=sourcedf.SmoothAltitude10-sourcedf.SmoothAltitude10.shift(periods=1)
    sourcedf['SmoothGradient10']=np.round(sourcedf.SmoothAltitude10.diff(periods=10)/sourcedf.SumDistance10,3)

    #If the Smoothgradient in a specific row is not a number but elevation and distxy is, then just set the gradient to this particular row's gradient (elevation/distxy)
    sourcedf.loc[(np.isnan(sourcedf['SmoothGradient10'])==True) & (np.isnan(sourcedf['Elevation'])==False) & (np.isnan(sourcedf['DistXY'])==False),'SmoothGradient10']= np.round(sourcedf.Elevation/sourcedf.DistXY,3)

    #Add a small amount of smoothing to the direction as well, not too much because we still need to pick up corners and turns
    sourcedf['SmoothDirection5']=np.round(sourcedf.Direction.rolling(window=5,min_periods=1).mean(),3)
    sourcedf['SmoothSpeed10'] = np.round(sourcedf.SumDistance10/sourcedf.SumDuration10,1)
    sourcedf['TrueRelwspeed10'] = np.round((np.cos(np.radians(sourcedf['SmoothDirection5'] - sourcedf['Winddirection'])) * sourcedf['Windspeedmps']),3)

    #Add some smoothing to the powerdata too so that we can track poweroutput intervals a bit more smoothly, especially for the WahooKickr
    sourcedf['SmoothWatts3']=np.round(sourcedf.Watts.rolling(window=3,min_periods=0).mean(),0)


    #Fudge the wind data for head and tail winds - for some reason if you don't fudge it it massively overestimates the power
    #and it does not do it consistently for head and tailwinds. So we adjust the headwind by a factor

    sourcedf['adjustedforhead'] = sourcedf.TrueRelwspeed10*fhw
    sourcedf['adjustedfortail'] = sourcedf.TrueRelwspeed10*ftw
    sourcedf['usehead'] = (sourcedf.TrueRelwspeed10<0) * 1.0
    sourcedf['usetail'] = (sourcedf.TrueRelwspeed10>=0) * 1.0
    sourcedf['Relwspeed10'] = sourcedf.adjustedforhead*sourcedf.usehead + sourcedf.adjustedfortail*sourcedf.usetail

    sourcedf.drop(columns=['adjustedforhead','adjustedfortail','usehead','usetail'],axis=1,inplace=True)


    addcalculatedpowerdata(sourcedf, riderweight, bikeweight, crr, rho, cd, fa)
    smoothcalculatedpowerdata(sourcedf,'CalculatedPower10','SmoothCP10','SmoothCW10','Duration',exfact)

    sourcedf.drop(
        columns=['PrevLat', 'PrevLong', 'PrevAlt', 'PrevTime','smoothalt'], axis=1, inplace=True)

    return sourcedf

# This function takes a pathname and a list of file names as input, and combines them all
# into a single CSV, with a number of additional calculated fields

#def readcyclecsv(pathname,filelist,riderweight, bikeweight, crr, rho, cd, fa, exfact,wspeedkph,wdirdeg,fhw,ftw):
def readcyclecsv(pathname,filelist,basedatafile):
    # pathname is a folder name
    # filelist is a list of files in the folder

    if pathname[:-1] != '/':
        pathname+='/'

    basedata,stops = readbasedata(basedatafile)

    filecounter = 0
    cycledata = pd.DataFrame()

    for file in filelist:
        try:
            rawdata = pd.read_csv(pathname+file)
        except Exception as e:
            print(f'{file} something went wrong {e}')
            continue

        #Get all the parameterdata from basedata
        matchfilename = file[4:-4]+'.'+file[1:4]  # this is a hack to get the file name back to the original raw file name, not the name as per the interim folder
        try:
            params = basedata[basedata.filename == matchfilename].iloc[0]
            targetwatts = params.targetwatts
            temperature = params.temperature
            wspeedkph = params.wspeedkph
            wdirdeg = params.wdirdeg
            airpressure = params.airpressure
            rho = params.rho
            riderweight = params.riderweight
            crr = params.crr
            bike = params.bike
            bikeweight = params.bikeweight
            cd = params.cd
            fa = params.fa
            exfact = params.exfact
            fheadw = params.fheadw
            ftailw = params.ftailw
            filecounter += 1
        except IndexError:
            print(matchfilename, ' not found in the basedata file. Default values will be used')
            try:
                params = basedata[basedata.filename == 'Generic'].iloc[0]
                targetwatts = params.targetwatts
                temperature = params.temperature
                wspeedkph = params.wspeedkph
                wdirdeg = params.wdirdeg
                airpressure = params.airpressure
                rho = params.rho
                riderweight = params.riderweight
                crr = params.crr
                bike = params.bike
                bikeweight = params.bikeweight
                cd = params.cd
                fa = params.fa
                exfact = params.exfact
                fheadw = params.fheadw
                ftailw = params.ftailw
                filecounter += 1
            except IndexError:
                print(matchfilename, ' not found, and default row "Generic" not found either. This file will be skipped')
                continue

        #Add calculated fields to the dataframe
        filedata=addcomputedcycledata(rawdata,riderweight, bikeweight, crr, rho, cd, fa, exfact,wspeedkph,wdirdeg,fheadw,ftailw)

        if filecounter == 0 :
            cycledata = filedata.copy(deep=True)
        else:
            cycledata=cycledata.append(filedata,ignore_index=True,sort=False)
        filecounter+=1
        print(len(filedata),'rows, total rows : ',len(cycledata),'.           File added : ',file)

    return cycledata

#This function returns a CSV file as a datafram
def getfinalcsvcycledata(filepath,filename):
    rawdata = pd.read_csv(filepath+filename,dtype={'Cadence' : np.float, 'HeartRate' : np.float})
    return rawdata

#This function will return a list of files containing a point within the specified bounding box
# List any file that contains a point within a bounding box
def listfilesingeobox(lat1,lat2,long1,long2,inputpath, outputpath):
    #lats and longs in degrees
    #inputpath is a file folder

    if lat1 > lat2 :
        lat3 = lat1
        lat1 = lat2
        lat2 = lat3

    if long1 > long2 :
        long3 = long1
        long1 = long2
        long2 = long3

    files = os.scandir(inputpath)
    results = []
    for file in files:
        inputfilename = file.name
        prefix = file.name[0:4]
        if file.name[-3:].upper() == 'CSV' and (prefix == '_gpx' or prefix == '_tcx' or prefix == '_fit'):
            print(f'Processing {file.name}')
            try:
               rawdata = pd.read_csv(file)
               pointsinbox = rawdata.RowId[rawdata['LatitudeDegrees'] >= lat1][rawdata['LatitudeDegrees'] <= lat2][
                   rawdata['LongitudeDegrees'] >= long1][rawdata['LongitudeDegrees'] <= long2]
               results.append([file.name,len(pointsinbox),len(rawdata)])
            except Exception as e:
                print(f'{file} something went wrong {e}')
                continue
    filelist = pd.DataFrame(results,columns=['Filename','MatchedPointcount','TotalPointCount'])
    outfilename='FilesCoveringLat'+str(lat1).replace('.','_')+'Long'+str(long1).replace('.','_')+'to'+str(lat2).replace('.','_')+'Long'+str(long2   ).replace('.','_')+'.csv'
    filelist.to_csv(outputpath+outfilename)
    return

# Determine runtype - returns Level, Climb or Descend
def runtype(elevation):
    if elevation >= 0.02:
        return 'Climb'
    elif elevation <= -0.02:
        return 'Descend'
    elif elevation < 0.2 and elevation > -0.02:
        return 'Level'

    return 'Not Known'

def addcomputedclimbdata(sourcedf):

    print('Calculating climb data on the full  dataset (for climbs, levels and descends) ....')

    # Add a column to indicate whether the row is level, climb or descend. This assumes that df.Elevation has already been populated
    sourcedf['RunType'] = sourcedf.SmoothElevation10.apply(runtype)

    #Get rid of single instances sandwiched by the same runtype, eg climb-climb-level-climb must become climb-climb-climb-climb

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf.loc[(sourcedf.nextruntype == sourcedf.prevruntype) & (sourcedf.RunType == "Level"), 'RunType'] = sourcedf['prevruntype']

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf.loc[(sourcedf.nextruntype == sourcedf.prevruntype) & (sourcedf.RunType == "Descend"), 'RunType'] = sourcedf['prevruntype']

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf.loc[(sourcedf.nextruntype == sourcedf.prevruntype) & (sourcedf.RunType == "Climb"), 'RunType'] = sourcedf['prevruntype']

    # Determine run start and run end
    # If the run type of the previous row and the run type of the current row differ, then it signifies a run start
    # or if the activity id is different - we can assume that the RunType value of the first row for a new activity
    # id will always be 'Not Known' so we don't have to write specific logic to pick up new activity id

    sourcedf['prevruntype'] = sourcedf.RunType.shift(1)
    sourcedf['RunStart'] = (sourcedf.RunType != sourcedf.prevruntype) * 1

    sourcedf['nextruntype'] = sourcedf.RunType.shift(-1)
    sourcedf['RunEnd'] = (sourcedf.RunType != sourcedf.nextruntype) * 1

    sourcedf.drop(columns=['prevruntype', 'nextruntype'], axis=1, inplace=True)

    # Calculate run id's
    # The run id will be equivalent to the rowid of the run's starting row
    # Just to make the logic here obvious - because only rows at the start of the run has a value of 1, the rest a value of 0,
    #       cumsum() will allocate the startrow id to all the entries in the same run

    sourcedf['RunId'] = sourcedf.RunStart.cumsum()

    # Now add columns for cumulative distance, duration, etc and cumulative averages by run

    sourcedf[['RunDistXY', 'RunDistXYZ', 'RunElevation', 'RunDuration']] = sourcedf.groupby(['RunId']).cumsum()[
        ['DistXY', 'DistXYZ', 'SmoothElevation10', 'Duration']]

    sourcedf['RunGradient'] = np.round((sourcedf.RunDistXYZ != 0) * sourcedf.RunElevation / sourcedf.RunDistXY,3)
    sourcedf['RunSpeedmps'] = np.round(sourcedf.RunDistXYZ / sourcedf.RunDuration,3)

    sourcedf['pedalstrokes'] = sourcedf.Cadence * sourcedf.Duration / 60
    sourcedf['RunPedalstrokes'] = sourcedf.groupby(['RunId']).cumsum()['pedalstrokes']
    sourcedf['RunCadence'] = np.round(sourcedf.RunPedalstrokes / sourcedf.RunDuration * 60, 1)

    sourcedf.drop(columns=['pedalstrokes'], axis=1, inplace=True)
    sourcedf['RunPedalstrokes'] = np.round(sourcedf.RunPedalstrokes,2)

    sourcedf['RunTotalWatts'] = sourcedf.groupby(['RunId']).cumsum()['Watts']
    sourcedf['RunAvgWatts'] = np.round(sourcedf.RunTotalWatts/sourcedf.RunDuration,2)

    sourcedf['RunSmoothCW10'] = sourcedf.groupby(['RunId']).cumsum()['SmoothCW10']
    sourcedf['RunSmoothCP10'] = np.round(sourcedf.RunSmoothCW10/sourcedf.RunDuration,2)

    return sourcedf


#####################################################################
##   THE CODE BELOW RELATES TO PROJECTIONS FROM A SUPPLIED ROUTE FILE
#####################################################################

# takes in a GPX file of a route and outputs a CSV file
# Must have latitude, longitude, altitude
def convertrouteGPX(input,output):

    error = False
    errorcount = 0
    lasterror = ''
    lines = 0

    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r'^({.*})', root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ''

    if root.tag != ns + 'gpx':
        print('Looking for root "gpx", but Unknown root found: ' + root.tag)
        return lines, error, errorcount, lasterror

    metadata = root.find(ns+ 'metadata')
    if not metadata:
        print('Unable to find "gpx.metadata"')
        return lines,error,errorcount,lasterror
    try:
        id = metadata.find(ns + 'time').text.strip()
        stripped = re.findall('\d', id)
        actid = '_' + ''.join(stripped)
        rowprefix=''.join(stripped)
    except:
        actid = ''
        rowprefix=''

    tracks = root.find(ns + 'trk')
    if not tracks:
        print('Unable to find "trk" under root')
        return lines, error, errorcount, lasterror

    columnsEstablished = False

    tracksegments = tracks.find(ns + 'trkseg')
    if not tracksegments:
        print('Unable to find "trkseg" under "trk"')
        return lines, error, errorcount, lasterror

    if columnsEstablished:
        fout.write('New Track Segment\n')

    for trackpoint in tracksegments.iter(ns + 'trkpt'):

        #print (trackpoint.get('lat'))

        lines += 1
        rowid = "{:0>7d}".format(lines)
        lasterror = ''

        latitude = ''
        longitude = ''
        altitude=''
        try:
            latitude = trackpoint.get('lat').strip()
        except:
            latitude = ''
            error = True
            errorcount += 1
            lasterror += 'latitude |'
        try:
            longitude = trackpoint.get('lon').strip()
        except:
            longitude = ''
            error = True
            errorcount += 1
            lasterror += 'longitude |'
        try:
            altitude = trackpoint.find(ns + 'ele').text.strip()
        except:
            altitude = ''
            error = True
            errorcount += 1
            lasterror += 'altitude |'

        if not columnsEstablished:
            filetype = 'gpx'
            fout = open(output, 'w')
            fout.write(','.join(
                ('RowId', 'ActivityId', 'LatitudeDegrees', 'LongitudeDegrees','AltitudeMeters')) + '\n')
            columnsEstablished = True
        fout.write(
            ','.join((rowid, actid, latitude, longitude, altitude)) + '\n')

    return lines, error, errorcount, lasterror

# Takes an inputfolder and converts all the GPX route files into a consistent output
def convertroutefilesbatch(inputpath, outputpath):
    files = os.scandir(inputpath)
    countGpx = 0
    results = []
    results.append(['Filename','Outputfile','Linecount','Errorfound','Errorcount','Errortext'])
    for file in files:
        inputfilename = file.name
        if file.name[-3:].upper() == 'GPX':
            outputfilename = '/_gpx' + ''.join(file.name)
            countGpx += 1
            cvinput = inputpath + '/' + inputfilename
            cvoutput = outputpath + '/' + outputfilename[0:-3] + 'csv'
            print('GPX : ',cvinput,'    -     ',cvoutput)
            lines, error, errorcount, lasterror = convertrouteGPX(cvinput, cvoutput)
            results.append([file.name,outputfilename[1:-3] + 'csv', lines, error, errorcount, lasterror])

        with open(outputpath+'/'+'___process_report.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for line in results:
                writer.writerow(line[i] for i in range(0,len(line)))
        f.close()

# Calculates the rolling, drag, gravity and accelerative components given specific geodata and a targeted max overall power consumption
def calcpowercomponentsfromrouteandtargetwatts(weight,crr,rho,cd,fa,speedmps,gradient,directiondeg,distance,wspeedkph,wdirdeg,fhw,ftw,targetwatts,maxallowedspeed):

    ######
    ######  PLEASE REMEMBER TO TAKE MAX ALLOWED SPEED INTO ACCOUNT
    ######

    g=9.8067  #gravity

    suppliedtargetwatts = targetwatts

    if suppliedtargetwatts > 600:
        targetwatts = 600   #A bit arbitrary for now

    if gradient >= 1:
        gradient /= 100.0   #we do this to cater for gradient that is expressed as 0.05 OR 5%

    if np.isnan(distance):
        distance = 0

    dirrad = np.radians(directiondeg)
    wdirrad = np.radians(wdirdeg)
    wspeedmps = wspeedkph/3.6

    #Calculate the power required to overcome rolling resistance:
    proll = g * np.cos(np.arctan(gradient)) * weight * crr * speedmps

    #Calculate the power required to overcome gravity
    pgrav = g * np.sin(np.arctan(gradient)) * weight * speedmps

    #Calculate the power required to overcome drag
    if np.isnan(wspeedmps) or np.isnan(dirrad) or np.isnan(wdirrad):
        relwspeedmps = speedmps
    else:
        relwspeedmps = np.cos(dirrad - wdirrad) * wspeedmps
    if relwspeedmps < 0 :
        adjustedwspeed = relwspeedmps*fhw
    else:
        adjustedwspeed = relwspeedmps*ftw


    pdrag = 0.5 * cd * fa * rho * (speedmps-adjustedwspeed)**2 * speedmps

    #If pdrag requires more than the available watts, then reduce the exitspeed to be within the required powerwindow
    #This needs some fresh thinking, the same can happen with gravity
    #This might all be resolved if we can get to a formula that use midpoint velocity rather than entry velocity
    #Maybe something around breaking and calculating per second and recalculating all parameters at the end of every second.....
    '''
    if pdrag > (targetwatts - proll - pgrav):
        airtogroundspeedfactor=((speedmps-adjustedwspeed)/speedmps)**2
        targetdragpower = targetwatts-proll-pgrav
        targetspeed = targetdragpower/(0.5*cd*fa*rho*airtogroundspeedfactor)
        if targetspeed < maxallowedspeed:
            maxallowedspeed = targetspeed
        #and let us for the time being assume that new dragpower is (olddragpower+targetdragpower) / 2
        pdrag = (pdrag+targetdragpower)/2
    '''

    # Now calculate the acceleration
    remainingwatts = targetwatts-(proll+pgrav+pdrag)

    acceleration = remainingwatts / weight / g

    if acceleration > 16.667:
        #Reckon it would be quite difficult to get from 0 to 60km/h in 30 seconds
        acceleration = 16.667

    rootcalc = speedmps ** 2 + 2 * acceleration * distance
    if rootcalc < 0:
        #print('Calculating time issue. speedmps = ', speedmps, '    acceleration = ', acceleration, '   distance = ', distance, ' ....',rootcalc)
        #this basically means that at the given acceleration, the distance required is less than the distance between the two points.
        #in this case for now we should just assume then that no acceleration or deceleration will be happening
        acceleration = 0
        rootcalc = speedmps ** 2 + 2 * acceleration * distance   #essentially speedmps**2 only

    if acceleration == 0 :
        time = distance/speedmps
    else:
        time = ((speedmps*-1) + np.sqrt(rootcalc)) / acceleration

    if np.isnan(time):
        time = 0

    #We will assume that time2 is the appropriate one for now
    exitspeed = speedmps+acceleration*time

    ######
    ######  MAX ALLOWED SPEED HACK - THIS SHOULD BE REPLACED WITH A RECALC OF EVERY POWER COMPONENT
    ######  AND THE MAX TARGET WATTS SHOULD THEN ALSO BE ADJUSTED SOMEHOW
    ######
    if exitspeed > maxallowedspeed:
        exitspeed = maxallowedspeed
        # Rolling and gravity power calcs stay the same
        # Drag stays the same because at this stage we are calculating drag based on the ENTRY speed, not the exit speed
        # Accelarative power has not yet been calculated and will be done after this conditional block

        time = distance/((speedmps+exitspeed)/2)
        acceleration = (exitspeed-speedmps)/time

    #Do the accelerative power equation - if the exit speed is lower than the entry speed then discard accelerative power
    #basically means the rider has braked, so the energy is lost (until we get KERS for bicycles)
    if exitspeed > speedmps:
        paccel = weight*g*(exitspeed-speedmps)/time
    else:
        paccel = 0


    ptotal = proll + pgrav + pdrag + paccel

    wtotal = ptotal*time

    closingbalance = suppliedtargetwatts - ptotal

    return {
    "maxallowedspeed": np.round(maxallowedspeed),
    "entryspeedmps": np.round(speedmps,3),
    "relwspeedmps": np.round(relwspeedmps,3),
    "adjustedwspeed": np.round(adjustedwspeed,3),
    "targetwatts": targetwatts,
    "prolling": np.round(proll,0),
    "pgravity": np.round(pgrav,0),
    "pdrag": np.round(pdrag,0),
    "remainingwatts": np.round(remainingwatts,0),
    "paccel": np.round(paccel,3),
    "ptotal": np.round(ptotal,3),
    "wtotal": np.round(wtotal,3),
    "acceleration": np.round(acceleration,5),
    "time": np.round(time,3),
    "exitspeed": np.round(exitspeed,3)
    }, closingbalance

# Calculates expected speed from gradient and target average watts into the datapoint (and at some stage also wind direction)
def addrouteperformance_old(sourcedf,riderweight,bikeweight,crr,rho,cd,fa,wspeedkph,wdirdeg,fhw,ftw,targetwatts):

    sourcedf['entryspeedmps'] = np.nan
    sourcedf['relwspeedmps'] = np.nan
    sourcedf['adjustedwspeed'] = np.nan
    sourcedf['exitspeed'] = np.nan
    sourcedf['time'] = np.nan
    sourcedf['targetwatts'] = np.nan
    sourcedf['prolling'] = np.nan
    sourcedf['pgravity'] = np.nan
    sourcedf['pdrag'] = np.nan
    sourcedf['remainingwatts'] = np.nan
    sourcedf['paccel'] = np.nan
    sourcedf['ptotal'] = np.nan
    sourcedf['wtotal'] = np.nan
    sourcedf['acceleration'] = np.nan


    g = 9.8067 #Gravity
    weight = riderweight+bikeweight

    dflen = len(sourcedf)

    entryspeed=0
    exitspeed = 0

    rowcount = 0
    closingbalance = 0
    suppliedtargetwatts = targetwatts

    for index,row in sourcedf.iterrows():
        if rowcount/1000.0 == round(rowcount/1000,0):
            print ('Processing row ',rowcount,' of ',dflen)

        rowcount +=1

        #Calculate power required to overcome rolling resistance, gravity and drag using
        #the given entry speed - slightly dodgy foundation, because the speed will change
        #over the duration of the segment because there will likely be acceleration but this
        #can be refined later. If the segments are all relatively short it shouldn't make too much of
        #a difference

        gradient = row.Gradient
        directiondeg = row.Direction
        distance = row.DistXYZ
        maxallowedspeed = row.MaxAllowedSpeed

        targetwatts = suppliedtargetwatts + closingbalance

        result,closingbalance = calcpowercomponentsfromrouteandtargetwatts(weight, crr, rho, cd, fa, entryspeed, gradient, directiondeg, distance, wspeedkph, wdirdeg, fhw, ftw, targetwatts,maxallowedspeed)

        entryspeed = result['exitspeed']

        sourcedf.loc[index, ['entryspeedmps','relwspeedmps','adjustedwspeed','targetwatts','prolling','pgravity','pdrag',
                            'paccel','ptotal','wtotal','remainingwatts','acceleration','time','exitspeed']] = [result['entryspeedmps'],
                            result['relwspeedmps'],result['adjustedwspeed'],result['targetwatts'],result['prolling'],result['pgravity'],
                            result['pdrag'],result['paccel'],result['ptotal'],result['wtotal'],result['remainingwatts'],
                            result['acceleration'],result['time'],result['exitspeed']]

    return sourcedf

def calcgeoendpoint(latitudedeg,longitudedeg,distancemeters):

    earthradius =   6371000  # meter
    latdiff = np.radians(df[curlatname]) - np.radians(df[prevlatname])
    longdiff = np.radians(df[curlongname]) - np.radians(df[prevlongname])
    lat1rad = np.radians(df[curlatname])
    lat2rad = np.radians(df[prevlatname])
    altdiff = df[curaltname]-df[prevaltname]

    a = np.sin(latdiff/2.0)**2 + np.cos(lat1rad)*np.cos(lat2rad)*np.sin(longdiff/2.0)**2
    c = 2*np.arctan2(np.sqrt(a),np.sqrt(1-a))
    d = np.round(earthradius*c,2) # distance in the xy plane
    d3 = np.round(np.sqrt(d*d+altdiff*altdiff),2) #distance in the 3 dimensional plane

    df[distxycolname] = d
    df[distxyzcolname] = d3

    return endlat, endlong

def addrouteperformance(sourcedf,riderweight,bikeweight,crr,rho,cd,fa,wspeedkph,wdirdeg,fhw,ftw,targetwatts,stops):

    #print('\n\n**********############ REMEMBER TO DO ***************##################')
    #print('**********\n**********    Get the interim latitude and longitudes right')
    #print('**********\n**********############ REMEMBER TO DO ***************##################\n\n')

    #set constants
    g = 9.8067
    weight = riderweight + bikeweight

    print('File has ',len(sourcedf),' rows. Total weight = ',weight,'. Targetwatts:',targetwatts,'cd/fa = ',cd,'/',fa,'fhw/thw = ',fhw,'/',ftw)

    #create a new dataframe that will store second by second performance data
    routeplancolumns = [
        'latitude',
        'longitude',
        'altitude',
        'direction',
        'gradient',
        'intervaldistance',
        'exitdistance',
        'speed',
        'duration',
        'elapsedduration',
        'averagespeedkmh',
        'gpslabel',
        'wattbalance',
        'proll',
        'pgrav',
        'pdrag',
        'paccel',
        'ptotal',
        'pbalance',
        'relativewindspeed',
        'adjustedwindspeed',
        'speedkph',
        'maxallowedspeed',
        'speedlimited'
    ]
    routeplan = pd.DataFrame(data=None,columns = routeplancolumns)

    #set the first set of values
    sourcerow = sourcedf[sourcedf.EntryDistance == 0].iloc[[0]]
    latitude = sourcerow.iloc[0]['LatitudeDegrees']
    longitude = sourcerow.iloc[0]['LongitudeDegrees']
    altitude = sourcerow.iloc[0]['AltitudeMeters']
    gradient = sourcerow.iloc[0]['Gradient']
    direction = sourcerow.iloc[0]['Direction']
    winddirection = sourcerow.iloc[0]['Winddirection']
    windspeed = sourcerow.iloc[0]['Windspeedmps']
    maxallowedspeed = sourcerow.iloc[0]['MaxAllowedSpeed']

    #Get the distance for the first rest stop
    if len(stops) > 0:
        stoprow = stops.iloc[[0]]
        restkm = np.int(stoprow.distancekm+1)
        restsecs = np.int(stoprow.durationmins*60+1)

    else:
        restkm = 999999
        restsecs = 0

    #calculate data per timeincrement
    deltat = 1  # timeincrement, should be set to 1 (second)
    paccel = 0
    speed = 0
    wattbalance = 0
    dist_exit = 0

    timeinsecs = 0
    maxtimeinsecs = 60 * 60 * 10

    while timeinsecs < maxtimeinsecs:

        if round(timeinsecs / 60.0 / 15.0, 0) == timeinsecs / 60.0 / 15.0:
            print(timeinsecs / 60.0,'minutes done ... ',datetime.datetime.now())

        # Calculate the power required to overcome rolling resistance for the given gradient and speed
        proll = g * np.cos(np.arctan(gradient)) * weight * crr * speed

        # Calculate the power required to overcome gravity
        pgrav = g * np.sin(np.arctan(gradient)) * weight * speed

        # Calculate the power required to overcome drag
        dirrad = np.radians(direction)
        wdirrad = np.radians(winddirection)
        if np.isnan(windspeed) or np.isnan(dirrad) or np.isnan(wdirrad):
            relativewindspeed = speedmps
        else:
            relativewindspeed = np.cos(dirrad - wdirrad) * windspeed
        if relativewindspeed < 0:
            adjustedwindspeed = relativewindspeed * fhw
        else:
            adjustedwindspeed = relativewindspeed * ftw
        pdrag = 0.5 * cd * fa * rho * (speed - adjustedwindspeed) ** 2 * speed

        #The power available for acceleration is equal to the target input power
        # plus the power surplus carried over from the previous row
        # less (or plus) the nett power for roll, gravity and drag
        remainingwatts = targetwatts + wattbalance - (proll+pgrav+pdrag)
        speedlimited = False
        #but if the entry speed is already exceeding the max allowed speed, the bike is breaking and there is no accelerative, decelerative power
        if speed >= maxallowedspeed:
            acceleration = speed-maxallowedspeed
            paccel = 0
            speedlimited = True
            speed_exit = maxallowedspeed
        elif speed <= maxallowedspeed:
            acceleration = remainingwatts / (weight * g)
            speed_exit = speed + acceleration * deltat
            if speed_exit > maxallowedspeed:
                acceleration = maxallowedspeed - speed
                speed_exit = maxallowedspeed
                speedlimited = True
            # Calculate the actual power spent on acceleration
            paccel = (speed_exit - speed) * g * weight
            # Recalculate the drag (assume linear reduction, thus (pdrag at start + pdrag at end times a half)
            # newpdrag = 0.5 * cd * fa * rho * (speed_exit - adjustedwindspeed) ** 2 * speed_exit
            # pdrag = (pdrag + newpdrag) / 2.0

        distance = (speed + speed_exit) / 2 * deltat
        dist_exit = dist_exit + distance


        speed = speed_exit
        wattbalance += targetwatts - (proll + pgrav + pdrag + paccel)

        averagespeedkmh = round(dist_exit/(timeinsecs+deltat)*3.6,1)
        if round(timeinsecs / 60.0 / 5.0, 0) == timeinsecs / 60.0 / 5.0:
            td = timeinsecs
            timeh = int(td/3600)
            timemin = int((td - timeh*3600)/60)
            timestring = '{:02d}'.format(timeh) + ':' + '{:02d}'.format(timemin)
            diststring = str(round(dist_exit/1000,1))+'km'
            gpslabel = timestring+'  -  '+diststring
        else:
            gpslabel=''


        #Add the row to the new dataframe now, NOT AFTER you have recalculated the power figures
        routeplan.loc[timeinsecs] = [latitude,longitude,altitude,direction,gradient,round(distance,3),round(dist_exit,1),
                                     round(speed,3), deltat,timeinsecs+deltat,averagespeedkmh,gpslabel,round(wattbalance,2),
                                     round(proll,2), round(pgrav,2),round(pdrag,2), round(paccel,2),
                                     round(proll+pgrav+pdrag+paccel,2), round(wattbalance,0), round(relativewindspeed,3),
                                     round(adjustedwindspeed,3),round(speed*3.6,1),maxallowedspeed,speedlimited]

        #Check to see if a rest stop needs to be added
        if int(dist_exit/1000) == int(restkm):
            dist_exit = dist_exit - distance  #we have to subtract the recently added distance and remember to add it back later
            td = timeinsecs
            timeh = int(td/3600)
            timemin = int((td - timeh*3600)/60)
            timestring = '{:02d}'.format(timeh) + ':' + '{:02d}'.format(timemin)
            diststring = str(round(dist_exit/1000,1))+'km'
            gpslabel = timestring+'  -  '+diststring
            gpslabel += '  {:2d}m'.format(int(restsecs/60))+'{:02d}s'.format(int(restsecs)-int(restsecs/60)*60)+' stop'
            routeplan.loc[timeinsecs] = [latitude, longitude, altitude, direction, gradient, 0,
                                         round(dist_exit, 1), 0, restsecs, timeinsecs + restsecs,
                                         averagespeedkmh, gpslabel, 0,0,0,0,0,0,0,0,0,0,0,0]
            timeinsecs += restsecs
            speed_exit = 0
            speed = 0
            # Get the distance for the next rest stop
            if len(stops[stops.distancekm>restkm]) > 0:
                stoprow = stops[stops.distancekm>restkm].iloc[[0]]
                restkm = np.int(stoprow.distancekm+1)
                restsecs = np.int(stoprow.durationmins*60+1)

            else:
                restkm = 999999
                restsecs = 0

        try:
            sourcerow = sourcedf[(sourcedf.EntryDistance <= dist_exit) & (sourcedf.ExitDistance > dist_exit)].iloc[[0]]
            timeinsecs += deltat
        except IndexError:
            timeinsecs = maxtimeinsecs + 1
            print('Completed')
        latitude = sourcerow.iloc[0]['LatitudeDegrees']
        longitude = sourcerow.iloc[0]['LongitudeDegrees']
        altitude =  sourcerow.iloc[0]['AltitudeMeters']
        gradient = sourcerow.iloc[0]['Gradient']
        direction = sourcerow.iloc[0]['Direction']
        winddirection = sourcerow.iloc[0]['Winddirection']
        windspeed = sourcerow.iloc[0]['Windspeedmps']
        maxallowedspeed = sourcerow.iloc[0]['MaxAllowedSpeed']


    return routeplan

def calcbrakingdata():
    #This is just a placeholder for some javascript code I found

    '''
    function
    compute_dist(form)
    {var
    velocity = form.velocity.value * 0.44704  --- the velocity input in the form is in miles per hour;
    A = form.A.value - 0;   --- A.value is the adhesion coefficient and is between 0 and 1 (0.85 for dry concrete, 0.55 for wet concrete, 0.35 for sand and 0.1 for ice
    R = form.R.value - 0;   --- R.value is the rolling resistance coefficient set at 0.014 for tarmac and ice, and at 0.3 for sand
    form.dist_metric.value = int_zero((velocity * velocity) / (20 * (A + R)) * 100) / 100 ;   --- stopping distance in meters
    form.dist_brit.value = int_zero(((velocity * velocity) / (20 * (A + R)) / .3048) * 100) / 100;}   --- stopping distance in feet


    // Function
    to
    return 0 if result is < 1
    function
    int_zero(x)
    { if (x < 1)
    return 0; else return parseInt(x, 10);

    What this function does not do is to take the effect of gravity into account - I don't know whether this makes a difference or not
    Is stopping distance from 30km/h amy different on a level road than on a downhill road with a 10% gradient??

    '''

    return

def addroutedirectiondata(sourcedf):

    sourcedf['nextdirection'] = sourcedf.Direction.shift(-1)

    sourcedf['clockwisedeg'] = np.abs(sourcedf.Direction - sourcedf.nextdirection)
    sourcedf.loc[sourcedf.Direction > sourcedf.nextdirection,'clockwisedeg'] = np.abs(360-sourcedf.Direction+sourcedf.nextdirection)
    sourcedf['anticlockwisedeg'] = 0
    sourcedf.loc[sourcedf.clockwisedeg > 0, 'anticlockwisedeg'] = 360-sourcedf.clockwisedeg

    sourcedf['TurnDirection'] = 'Straight'
    sourcedf.loc[(sourcedf.anticlockwisedeg <= sourcedf.clockwisedeg) & (sourcedf.anticlockwisedeg > 0),'TurnDirection'] = 'Left'
    sourcedf.loc[sourcedf.anticlockwisedeg > sourcedf.clockwisedeg,'TurnDirection'] = 'Right'

    sourcedf['Turndeg'] = sourcedf.clockwisedeg
    sourcedf.loc[sourcedf.TurnDirection == 'Left','Turndeg'] = sourcedf.anticlockwisedeg

    maxtheoreticalspeed = round(65/3.6,1)    # for now we set the maximum allowed speed to 70km/h. This algorithm is not for Tour De France cyclist ha ha ha
    sourcedf['MaxAllowedSpeed'] = maxtheoreticalspeed
    sourcedf.loc[sourcedf.Turndeg <= 95,'MaxAllowedSpeed'] = np.round(((110-sourcedf.Turndeg)/110)**1.5*maxtheoreticalspeed,5)
    sourcedf.loc[sourcedf.Turndeg > 95, 'MaxAllowedSpeed'] = 1

    sourcedf.drop(columns=['nextdirection','clockwisedeg','anticlockwisedeg'],inplace=True,axis=1)

    return sourcedf

# Removes points in the route file that are too close to each other
def reducecrowdedpoints(sourcedf):

    tooclose = 2
    rowcount = len(sourcedf)
    newrowcount = 0
    while rowcount != newrowcount:
        rowcount = len(sourcedf)

        sourcedf['tooclosetoprevious'] = sourcedf.DistXYZ.apply(lambda x: 1 if x < tooclose else 0)
        sourcedf['tooclosetonext'] = (sourcedf.DistXYZ.shift(-1)).apply(lambda x: 1 if x < tooclose else 0)

        #Drop all rows where previous point and next point are both within "tooclose" metres
        rowstodrop = sourcedf[(sourcedf.tooclosetoprevious == 1) & (sourcedf.tooclosetonext == 1)].index
        sourcedf.drop(rowstodrop,inplace=True)
        newrowcount = len(sourcedf)

        if newrowcount == rowcount:
           #if the new rowcount is the same as the old rowcount, then all the rows with points too close
           #  on either side has been eliminated.There may still be rows where the points is too close to the previous point,
           #  eliminate these rows now
           rowstodrop = sourcedf[(sourcedf.tooclosetoprevious == 1)].index
           sourcedf.drop(rowstodrop, inplace=True)

           newrowcount = len(sourcedf)

           if newrowcount != rowcount:
               # Recalculate all the geo distances
               addgeodistanceindf(sourcedf, curlatname='LatitudeDegrees', prevlatname='PrevLat',
                    curlongname='LongitudeDegrees', prevlongname='PrevLong', curaltname='AltitudeMeters',
                    prevaltname='PrevAlt', distxycolname='DistXY', distxyzcolname='DistXYZ')

           sourcedf.drop(columns=['tooclosetoprevious','tooclosetonext'], axis=1,inplace=True)


# Takes the basic plan data and add a few computed columns : xy distance, xyz distance, gradient and runs, and so forth
# and call the required functions to add targeted power and velocity data
def addcomputedroutedata(sourcedf,riderweight, bikeweight, crr, rho, cd, fa, exfact, wspeedkph, wdirdeg, fhw, ftw, targetwatts,stops):

    sourcedf['LatitudeRad'] = np.radians(sourcedf['LatitudeDegrees'])
    sourcedf['LongitudeRad'] = np.radians(sourcedf['LongitudeDegrees'])

    sourcedf[['PrevLat','PrevLong','PrevAlt']] = sourcedf[['LatitudeDegrees','LongitudeDegrees','AltitudeMeters']].shift(periods=1)

    addgeodistanceindf(sourcedf, curlatname = 'LatitudeDegrees', prevlatname = 'PrevLat', curlongname = 'LongitudeDegrees',
                       prevlongname = 'PrevLong', curaltname = 'AltitudeMeters', prevaltname = 'PrevAlt',
                       distxycolname = 'DistXY', distxyzcolname = 'DistXYZ')

    #Drop all rows where the xy distance = 0 (they are spurious and interfere with the smoothing calculations)
    rowstodrop = sourcedf[sourcedf.DistXY == 0].index
    sourcedf.drop(rowstodrop,inplace=True)

    #Recalculate all the geo distances
    addgeodistanceindf(sourcedf, curlatname = 'LatitudeDegrees', prevlatname = 'PrevLat', curlongname = 'LongitudeDegrees',
                       prevlongname = 'PrevLong', curaltname = 'AltitudeMeters', prevaltname = 'PrevAlt',
                       distxycolname = 'DistXY', distxyzcolname = 'DistXYZ')


    #Remove rows where the xyz distance is too close to each other - no point should be closer than 5m to the next point
    reducecrowdedpoints(sourcedf)

    #Add running total of distance
    sourcedf['EntryDistance'] = sourcedf.DistXYZ.cumsum().apply(lambda x : 0 if np.isnan(x) == True else x)
    sourcedf['ExitDistance'] = sourcedf.EntryDistance.shift(-1)

    alt=sourcedf['AltitudeMeters'].astype(float)-sourcedf['PrevAlt'].astype(float)

    sourcedf['Elevation']=alt

    sourcedf['Direction'] = np.round(np.degrees(np.arctan2((sourcedf['LongitudeDegrees'] - sourcedf['PrevLong']),
                                                  (sourcedf['LatitudeDegrees'] - sourcedf['PrevLat']))).apply(lambda x: x if x >= 0 else 360 + x),0)
    sourcedf['Direction'] = sourcedf.Direction.shift(-1)
    sourcedf['Gradient'] = np.round((sourcedf['Elevation']/sourcedf['DistXY']).apply(lambda x: 0 if x == np.inf else 0 if x == -np.inf else x),3)
    sourcedf['Gradient'] = sourcedf.Gradient.shift(-1)

    #Make sure that all gradients are set to a number (set to 0 if not a number)
    sourcedf['Gradient']=sourcedf['Gradient'].apply(lambda x: 0 if np.isnan(x) == True else x)

    #Determine direction changes so that bicycle speed can be appropriately controlled
    addroutedirectiondata(sourcedf)


    wspeedmps = np.round(wspeedkph/3.6,1)
    sourcedf['Windspeedmps'] = wspeedmps
    sourcedf['Winddirection'] = wdirdeg


    routeplan = addrouteperformance(sourcedf, riderweight, bikeweight, crr, rho, cd, fa, wspeedkph, wdirdeg, fhw, ftw, targetwatts,stops)

    sourcedf.drop(
       columns=['PrevLat', 'PrevLong', 'PrevAlt', 'LatitudeRad', 'LongitudeRad'], axis=1, inplace=True)

    #Add summarised cumulative average speed, average power columns
    routeplan['moveduration'] = routeplan.duration.apply(lambda x: x if x == 1 else 0)
    routeplan['cumwork'] = routeplan.ptotal.cumsum()
    routeplan['moveelapsedduration'] = routeplan.moveduration.cumsum()
    routeplan['avcumpower'] = np.round((routeplan.cumwork.astype(float)/(routeplan.moveelapsedduration.astype(float))),1)
    routeplan['avmovespeedkph'] = np.round((routeplan.exitdistance.astype(float))/(routeplan.moveelapsedduration.astype(float))*3.6,1)
    routeplan['avoverallspeedkph'] = np.round((routeplan.exitdistance.astype(float))/(routeplan.elapsedduration.astype(float))*3.6,1)

    return sourcedf,routeplan

# This function takes a pathname and a list of file names as input, and outputs individual files
# with calculated fields and targeted power and speed data, based on overall average target wattage
#def createroutetargetsfromavgwatts(pathname,filelist,outputpath,riderweight, bikeweight, crr, rho, cd, fa, exfact,wspeedkph,wdirdeg,fhw,ftw,targetwatts):
def createroutetargetsfromavgwatts(pathname, filelist, outputpath, basedatafile):
    # pathname is a folder name
    # filelist is a list of files in the folder

    if pathname[:-1] != '/':
        pathname+='/'

    filecounter = 0

    basedata, routestops = readbasedata(basedatafile)

    #Create the training files one by one
    for file in filelist:
        try:
            rawdata = pd.read_csv(pathname+file)
        except Exception as e:
            print(f'{file} something went wrong {e}')
            continue

        #Get all the parameterdata from basedata
        matchfilename = file[4:-4]+'.'+file[1:4]  # this is a hack to get the file name back to the original raw file name, not the name as per the interim folder
        try:
            params = basedata[basedata.filename == matchfilename].iloc[0]
            targetwatts = params.targetwatts
            temperature = params.temperature
            wspeedkph = params.wspeedkph
            wdirdeg = params.wdirdeg
            airpressure = params.airpressure
            rho = params.rho
            riderweight = params.riderweight
            crr = params.crr
            bike = params.bike
            bikeweight = params.bikeweight
            cd = params.cd
            fa = params.fa
            exfact = params.exfact
            fheadw = params.fheadw
            ftailw = params.ftailw
            filecounter += 1
        except:
            print(matchfilename, ' not found in the basedata file. A training route will not be created for this file')
            continue

        #get all the stops from the basedata
        try:
            stops = routestops[routestops.filename == matchfilename]

        except:
            print(matchfilename, ' something went wrong accessing the basedata routestops worksheet. No stops will be scheduled')

        if len(stops) == 0:
            print(matchfilename,' no stops will be scheduled')


        #Add calculated fields to the dataframe
        filedata,routeplan=addcomputedroutedata(rawdata,riderweight, bikeweight, crr, rho, cd, fa, exfact,wspeedkph,wdirdeg,fheadw,ftailw,targetwatts,stops)

        # Use the below code if you want to create a result file per input file
        filecounter+=1
        outputfilename = '/_Train' + ''.join(file)
        try:
            filedata.to_csv(outputpath+outputfilename)
            print(len(filedata),'rows,            File added : ',file)
        except:
            print('Did not save ',outputfilename)

        routeplanfilename = '/_Routeplan' + ''.join(file)
        try:
            routeplan.to_csv(outputpath + routeplanfilename)
            print(len(routeplan),'rows,            File added : ',routeplanfilename,' Total duration: ',
                round(routeplan.duration.sum()/60,1),'min.  Total distance: ',
                round(routeplan.exitdistance.max()/1000,1),'km.  Average power: ',round(routeplan.ptotal.mean(),1))
        except:
            print('Did not save',routeplanfilename)

        # Use the below code code if you want to create a single dataframe across all files and return the dataframe
        '''
        if filecounter == 0 :
            cycledata = filedata.copy(deep=True)
        else:
            cycledata=cycledata.append(filedata,ignore_index=True,sort=False)
        filecounter+=1
        print(len(filedata),'rows, total rows : ',len(cycledata),'.           File added : ',file)
        '''

    return

def readbasedata(filepathandname):
    dtypes = {
        'filename': np.str,
        'ridedate': np.datetime64,
        'temperature': np.float,
        'wspeedkph': np.float,
        'wdirdeg': np.float,
        'airpressure': np.float,
        'rho': np.float,
        'bike': np.str,
        'bikeweight': np.float,
        'riderweight': np.float,
        'cd': np.float,
        'fa': np.float,
        'crr': np.float,
        'exfact': np.float,
        'fheadw': np.float,
        'ftailw': np.float,
        'targetwatts': np.float
    }

    stopdtypes = {
        'filename': np.str,
        'distancekm': np.float,
        'durationmins': np.float
    }

    df = pd.read_excel(io=filepathandname, sheet_name = 'basedata', header = 0, dtype = dtypes, parse_dates = ['ridedate'])

    stops = pd.read_excel(io=filepathandname, sheet_name = 'routestops', header = 0, dtype = stopdtypes)

    return df,stops
