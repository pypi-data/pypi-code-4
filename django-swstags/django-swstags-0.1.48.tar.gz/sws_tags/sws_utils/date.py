import olap.xmla.xmla as xmla
import simplejson
import types
from django.utils.dateparse import parse_datetime
import pytz
from pytz import timezone, utc
from suds import WebFault
import memcache
from international.models import *
import json
import types
from types import *
import re
import string
from datetime import date, datetime, timedelta
import time
from django.conf import settings
from django.utils.datastructures import SortedDict

from sws_tags.sws_utils.cube_utils import *
from sws_tags.sws_utils.__init__ import *

granularity=[
    ('Time','Minute Field','Minute Field'), # 0
    ('Time','Ten Minutes','Ten Minutes'),   # 1
    ('Time','Hour Half','Hour Half'),       # 2
    ('Time','Hour Field','Hour Field'),     # 3
    ('Time','Day Quarter','Day Quarter'),   # 4
    ('Time','Day Half','Day Half'),         # 5
    ('Date','Day Complete','Day Complete'),       # 6
    ('Date','Week Complete','Week Complete'),     # 7
    ('Date','Month Complete','Month Complete'),   # 8
    ('Date','Year Complete','Year Complete'),      # 9
    ('Date','Date Complete','Date Complete')
    ]

def strToDatetime(date_str):
    date_str = str(date_str)
    year = date_str[0:4]
    month = date_str[5:7]
    day = date_str[8:10]
    hour = date_str[11:13]
    minute = date_str[14:16]
    date = datetime(int(year),int(month),int(day),int(hour),int(minute),00)
    return date


def intToGMT(number):

    number = int(number)

    if number > 0:
        GMT = 'Etc/GMT-'+str(number)
    elif number<0:
        number = str(number)
        number = number.replace('-','')
        GMT = 'Etc/GMT+'+number
    else:
        GMT = 'Etc/GMT'
   
    return GMT    

def updateDateTz(request_data):



    # print 'ok--------->',request_data['user_tz']

    # try:    
    #     tz_adjustement = int(request_data['user_tz']) + int(request_data ['system_tz'])
    # except:
    #     tz_adjustement = int(request_data ['system_tz'])

    # request_data['tz_adjustement'] = tz_adjustement

    # ########stoneworktz
    # tz_utc = (datetime.now() - datetime.utcnow())+ timedelta(seconds=1)  

    # time_zone_sw = intToGMT(tz_utc.seconds/3600)

    # stonework_tz = pytz.timezone(time_zone_sw)  
    # stonework = stonework_tz.localize(datetime.now())
    # ######################

    # time_zone_user = intToGMT(tz_adjustement)
    
    gap_system = request_data['system_tz'].replace('Etc/GMT','')
    gap_user = request_data['user_tz'].replace('Etc/GMT','')
    # request_data['tz_adjustement'] = int(gap_system) - int(gap_user)
    request_data['tz_adjustement'] = gap_user

    selected_tz = pytz.timezone(request_data['user_tz'])

    fd = strToDatetime(request_data ['from_Date'])
    td  = strToDatetime(request_data['to_Date'])

    from_dsn = selected_tz.localize(fd)
    to_dsn = selected_tz.localize(td)

    # from_dsn = selected_tz.normalize(stonework.astimezone(from_date_select))
    # to_dsn = selected_tz.normalize(stonework.astimezone(to_date_select))

    request_data ['from_Date_user'] = request_data ['from_Date']
    request_data ['to_Date_user'] =  request_data ['to_Date']

    request_data ['from_Date_tz'] = datetime( from_dsn.year,from_dsn.month,from_dsn.day,from_dsn.hour,from_dsn.minute,from_dsn.second,tzinfo=selected_tz)
    request_data ['to_Date_tz'] = datetime( to_dsn.year,to_dsn.month,to_dsn.day,to_dsn.hour,to_dsn.minute,to_dsn.second,tzinfo=selected_tz)


    # print '************************************************************************************************************'
    # # print 'tz_adjustement',request_data['tz_adjustement']
    # # print 'user tz----->',request_data ['user_tz']
    # # print 'system_tz--->',request_data ['system_tz']
    # # print 'selected_tz',selected_tz
    # print 'fd----------->',fd
    # print 'td----------->',td
    # print 'from_dsn----->',from_dsn
    # print 'to_dsn------->',to_dsn
    # print 'FROM DATE request_data--->',request_data['from_Date']
    # print 'TO DATE request_data----->',request_data['to_Date']
    # print '************************************************************************************************************'

def correspondGranularity(request_data):

    if (isinstance(request_data['from_Date'],str)) == True:
        request_data['from_Date'] = unicode(request_data['from_Date'])
        request_data['to_Date'] = unicode(request_data['to_Date'])

    if (isinstance(request_data['from_Date'],unicode)) == False: 
        from_date = request_data['from_Date']
        to_date = request_data['to_Date']
    else:

        if (isinstance(request_data['from_Date'],unicode)): 
            year = str(request_data['from_Date'])[0:4]
            month = str(request_data['from_Date'])[5:7]
            day = str(request_data['from_Date'])[8:10]
            hour = str(request_data['from_Date'])[11:13]
            minute = str(request_data['from_Date'])[14:15]
            from_date = datetime(int(year),int(month),int(day),int(hour),int(minute),00)

        if (isinstance(request_data['to_Date'],unicode)): 
            year = str(request_data['to_Date'])[0:4]
            month = str(request_data['to_Date'])[5:7]
            day = str(request_data['to_Date'])[8:10]
            hour = str(request_data['to_Date'])[11:13]
            minute = str(request_data['to_Date'])[14:15]
            to_date = datetime(int(year),int(month),int(day),int(hour),int(minute),00)
    from_seg=(time.mktime(from_date.timetuple()))
    to_seg=(time.mktime(to_date.timetuple()))
    hour = int((to_seg - from_seg)/3600)

    if len(str((request_data['from_Date'])))==16:
        base_date = str(request_data['from_Date'])+':00'
    else:
       base_date = str(request_data['from_Date']) 


    granularity_index = 0

    if hour < 1: 
        granularity_index = 1 #Minute Field 
        request_data['base_Date'] = base_date[:-11]

    elif hour <= 2:
        granularity_index = 1 #Ten Minutes
        request_data['base_Date'] = base_date[:-11]

    elif hour <= 12:
        granularity_index = 2 # Hour Half
        request_data['base_Date'] = base_date[:-11]

    elif hour <= 24: 
        granularity_index = 3 # Hour Field 
        request_data['base_Date'] = base_date[:-11]

    elif hour <= 72:
        granularity_index = 4 # Day quarter
        request_data['base_Date'] = base_date[:-11]

    elif hour <= 168:
        granularity_index = 5 # Day half 
        request_data['base_Date'] = base_date[:-11]

    elif hour <= 744:
        granularity_index = 6 # Day Field
        request_data['base_Date'] = base_date[:-11]

    elif hour <=4464:
        granularity_index = 7 # Week Field
        request_data['base_Date'] = base_date[:-14]

    elif hour <=8760:
        granularity_index = 8 # Month Field 
        request_data['base_Date'] = base_date[:-14] 

    else:
        granularity_index = 9 # Year Field
        request_data['base_Date'] = base_date[:-17]



    if granularity_index == 5:
        granularity_index =4 

    # if request_data ['int_compare'] == 'ON':   for first load higstoc by all data
    #     granularity_index = 6

    return granularity_index


def numberHoursByGranularity(granularity):

    if granularity ==1:
        hour = 1
        # hour = 1
    elif granularity == 2:
        hour = 3
        # hour = 12
    elif granularity == 3:
        # hour = 12
        hour =24
    elif granularity == 4:
        # hour = 24
        # hour = 72
        hour = 168
    elif granularity == 5:
        # hour = 72
        hour = 168
    elif granularity == 6:
        # hour = 168
        hour = 744
    elif granularity == 7:
        hour = 744
        # hour = 4464
    elif granularity == 8:
        hour = 4464
        # hour = 8760
    else: 
        hour = 8760
        # hour = 999999

    return hour


def adjustementGranularity(request_data,col_cube): 

    if request_data['agrupation_data'].find('-')>=0:
        granularity_adjustement = int(request_data['agrupation_data'].replace('-',''))*-1     
    else:
        granularity_adjustement = int(request_data['agrupation_data'].replace('-',''))
    granularity_index = correspondGranularity(request_data)
   
    if request_data['int_compare'] == 'ON':
        if granularity_adjustement > 2:
            granularity_adjustement = 2
        if granularity_adjustement < -2:
            granularity_adjustement = -2


    index = granularity_index + granularity_adjustement
    index_col = index
    if index_col>7:
        index_col = 7
    if index_col <1:
        index_col = 1

    if index_col < 6:
        col_cube.append(granularity[6]) #add column date field 

    # #TODOMAS
    # if index_col > 5:
    #     col_cube.append(granularity[10])
    #     request_data['base_Date'] = ''
    # else:
    
    col_cube.append(granularity[index_col])

    request_data['granularity_text'] = granularity[index_col][2].replace('Field','')
    request_data['granularity_text'] = request_data['granularity_text'].replace('Complete','') 

    if request_data['granularity_text'] == 'Hour Half':
        request_data['granularity_text'] = 'Half Hour'
    elif request_data['granularity_text'] == 'Day Half':
        request_data['granularity_text'] = 'Half Day'


    request_data ['granularity_index'] = index


    ##Calculate date previous

    if (isinstance(request_data['from_Date'],unicode)) == False: 
        from_date = request_data['from_Date']
        to_date = request_data['to_Date']
    else:

        if (isinstance(request_data['from_Date'],unicode)): 
            year = str(request_data['from_Date'])[0:4]
            month = str(request_data['from_Date'])[5:7]
            day = str(request_data['from_Date'])[8:10]
            hour = str(request_data['from_Date'])[11:13]
            minute = str(request_data['from_Date'])[14:16]
            request_data['from_Date'] = datetime(int(year),int(month),int(day),int(hour),int(minute),00)

        if (isinstance(request_data['to_Date'],unicode)): 
            year = str(request_data['to_Date'])[0:4]
            month = str(request_data['to_Date'])[5:7]
            day = str(request_data['to_Date'])[8:10]
            hour = str(request_data['to_Date'])[11:13]
            minute = str(request_data['to_Date'])[14:16]
            request_data['to_Date'] = datetime(int(year),int(month),int(day),int(hour),int(minute),00)

    if request_data['int_forecast'] == 'OFF':
        forecast = 0
    else:
        forecast = 1

    hours_granularity = numberHoursByGranularity(granularity_index+forecast)


    
    request_data['dif_date'] = timedelta(hours=hours_granularity)
    request_data['from_Date_previous'] = request_data['from_Date'] - request_data['dif_date']
    request_data['to_Date_previous'] = request_data['from_Date_previous']  + request_data['dif_date'] - timedelta(seconds = 1)


def formatDateCubeComplete(date):
    date=str(date).replace(' ','T')
    return date

def formatDateCube(date):
    date=str(date).replace('-','').replace(' ','').replace(':','')
    len_date = len(date)
    if len_date==14:
        date = date[0:-2]
    while len(date)<14:
        date = date + '0'
    return date

def formatDateCubeDate(date):
    date=str(date).replace('-','').replace(' ','').replace(':','')
    len_date = len(date)
    if len_date==14:
        date = date[0:len_date-2]
    while len(date)<14:
        date = date + '0'


    if date[8:12] == '2359':
        date_int = int(date[0:8])+1
        date = str(date_int)+'000000'
    return date


def selectGranularity(request_data,col_cube):
    dif_date = int(formatDateCube(request_data ['to_Date'])) - int(formatDateCube(request_data ['from_Date']))
    range_date = ''

    if dif_date <= 10000:
        range_date = 'ten minutes'
        col_cube.append(('timedimension',range_date))

    elif dif_date <= 30000:
        range_date= 'hour half'
        col_cube.append(('timedimension',range_date))
        
    elif dif_date <= 240000:
        range_date= 'hour'
        col_cube.append(('timedimension',range_date))
        
    # elif dif_date <= 1680000:
    #     range_date= 'fecha'
    #     col_cube.append(('cdrfint',range_date))
        
    else:
        range_date= 'fecha'
        col_cube.append(('cdrfint',range_date))




def selectDatePrevious(request_data):

    from_seg=(time.mktime(from_date.timetuple()))
    to_seg=(time.mktime(to_date.timetuple()))
    hour = int((to_seg - from_seg)/3600)

    request_data['to_Date'] = str(request_data['to_Date']) 
    request_data['from_Date'] = str(request_data['from_Date']) 

    
    if dif_date <= 10000: #'hour'
        request_data['dif_date']  = 1
        hour = str(int(request_data['from_Date'][11:13]) - 1)
        if len(hour)==1:
            hour = '0'+hour
        new_hour = request_data['from_Date'][0:11] + hour + request_data['from_Date'][13:]
        request_data['from_Date_previous'] = new_hour

        hour = str(int(request_data['to_Date'][11:13]) - 1)
        if len(hour)==1:
            hour = '0'+ hour
        new_hour = request_data['to_Date'][0:11] + hour + request_data['to_Date'][13:]
        request_data['to_Date_previous'] = new_hour


    elif dif_date <= 30000:
        hour = str(int(request_data['from_Date'][11:13]) - 3)
        if len(hour)==1:
            hour = '0'+hour
        new_hour = request_data['from_Date'][0:11] + hour + request_data['from_Date'][13:]
        request_data['from_Date_previous'] = new_hour

        hour = str(int(request_data['to_Date'][11:13]) - 3)
        if len(hour)==1:
            hour = '0'+ hour
        new_hour = request_data['to_Date'][0:11] + hour + request_data['to_Date'][13:]
        request_data['to_Date_previous'] = new_hour
        request_data['dif_date']  = 3
        
    elif dif_date <= 1000000:
        day = str(int(request_data['from_Date'][8:10]) - 1)
        if len(day)==1:
            day = '0'+day
        new_date = request_data['from_Date'][0:8] + day + request_data['from_Date'][10:]
        request_data['from_Date_previous'] = new_date

        day = str(int(request_data['to_Date'][8:10]) - 1)
        if len(day)==1:
            day = '0'+day
        new_date = request_data['to_Date'][0:8] + day + request_data['to_Date'][10:]
        request_data['to_Date_previous'] = new_date
        request_data['dif_date']  = 24

    elif dif_date <= 6230000 :

        day = str(int(request_data['from_Date'][8:10]) - 7)
        if len(day)==1:
            day = '0'+day
        new_date = request_data['from_Date'][0:8] + day + request_data['from_Date'][10:]
        request_data['from_Date_previous'] = new_date

        day = str(int(request_data['to_Date'][8:10]) - 7)
        if len(day)==1:
            day = '0'+day
        new_date = request_data['to_Date'][0:8] + day + request_data['to_Date'][10:]
        request_data['to_Date_previous'] = new_date
        request_data['dif_date']  = 168
        
    else:
        if int(request_data['from_Date'][5:7]) ==1:
            anio = str(int(request_data['from_Date'][:4]) - 1)
            new_date = anio + '-12-'+request_data['from_Date'][8:]
            request_data['from_Date_previous'] = new_date

            anio = str(int(request_data['to_Date'][:4]) - 1)
            new_date = anio + '-12-'+request_data['to_Date'][8:]
            request_data['to_Date_previous'] = new_date
            request_data['dif_date']  = 5040
        else:
            mes = str(int(request_data['from_Date'][5:7]) - 1)
            if len(mes)==1:
                mes = '0'+mes
            new_date = request_data['from_Date'][0:5] + mes + request_data['from_Date'][7:]
            request_data['from_Date_previous'] = new_date

            mes = str(int(request_data['to_Date'][5:7]) - 1)
            if len(mes)==1:
                mes = '0'+mes
            new_date = request_data['to_Date'][0:5] + mes + request_data['to_Date'][7:]
            request_data['to_Date_previous'] = new_date
            request_data['dif_date']  = 5040
