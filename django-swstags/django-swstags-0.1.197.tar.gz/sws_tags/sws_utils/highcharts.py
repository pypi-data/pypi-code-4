#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
'''
highcharts.py

Highcharts utility library

Created by SWS on 2012-09-11.
Copyright (c) 2012 StoneWorkSolutions. All rights reserved.
'''

import random
from datetime import date, datetime, timedelta
# from dateutil.relativedelta import relativedelta
import time
import math
import hashlib

from sws_tags.sws_utils.cube_utils import *
from sws_tags.sws_utils.cube import *
from sws_tags.sws_utils.messages import *

def palette_color(name):

	dic_colors={
		'blue'   :['#00FFFF', '#729FCF', '#00008B'],
		'red'    :['#EF2929', '#FF0000', '#A40000'],
		'green'  :['#8AE234', '#006400', '#00FF00'],
		'gray'   :['#2F4F4F', '#000000', '#808080'],
		'yellow' :['#FFFF00', '#BDB77F', '#FCE94F'], #C4A05F
		'orange' :['#FFA07A', '#FF4500', '#F57900'],
		'pink'   :['#FFB6C1', '#FF1493', '#FF69B4'],
		'purple' :['#AD7FA8', '#800080', '#9400D3'],
		'brown'  :['#DEB887', '#8B4513', '#C17D11'],
		'white'  :['#FFFFFF', '#778899', '#C0C0C0'],
	}
	colors = ['blue','red','green','gray','yellow','orange','pink','purple','brown','white']

	name = name.replace('ASR','')
	name = name.replace('CALLS','')
	name = name.replace('INCOME','')
	name = name.replace('MINUTES','')
	name = name.replace('MARGIN','')

	# index=hash(name)%len(colors)

	index =int(hashlib.md5(name).hexdigest(),16)%len(colors)
	color=colors[index]

	for k,v in dic_colors.items():
		if k == color:
			c = v[0]
	return c


def paletteColor(name,spectrum):
		# 'combi0'	:['#FF00D1','#00FFD1','#FFA200'],#pink
		# 'combi1'	:['#FFA200','#048000','#9BF50A'],#orange
		# 'combi2'	:['#9BF50A','#FF00D1','#00FFD1'],#green
		# 'combi3'	:['#FFFFFF','#01FE2A','#FF0000'],#white
		# 'combi4'	:['#0066FF','#F3FF00','#FFFFFF'],#blue
		# 'combi5'	:['#01FE2A','#FF0000','#0066FF'],#green
		# 'combi6'	:['#048000','#9BF50A','#FF00D1'],#green2
		# 'combi7'	:['#00FFD1','#FFA200','#048000'],#blue2
		# 'combi8'	:['#FF0000','#0066FF','#F3FF00'],#red
		# 'combi9'	:['#F3FF00','#FFFFFF','#01FE2A']#yellow
	dic_colors={
		'blue'   :['#00FFFF', '#729FCF', '#00008B'],
		'red'    :['#EF2929', '#FF0000', '#A40000'],
		'green'  :['#8AE234', '#006400', '#00FF00'],
		'gray'   :['#2F4F4F', '#000000', '#808080'],
		'yellow' :['#FFFF00', '#BDB77F', '#FCE94F'], #C4A05F
		'orange' :['#FFA07A', '#FF4500', '#F57900'],
		'pink'   :['#FFB6C1', '#FF1493', '#FF69B4'],
		'purple' :['#AD7FA8', '#800080', '#9400D3'],
		'brown'  :['#DEB887', '#8B4513', '#C17D11'],
		'white'  :['#FFFFFF', '#778899', '#C0C0C0'],
	}
	colors = ['blue','red','green','gray','yellow','orange','pink','purple','brown','white']


	# dic_colors2={
	# 	'combi0'	:['#FF0000','#FF8484','#F3FF00'],#red
	# 	'combi1'	:['#FFA200','#FFCD78','#9BF50A'],#orange
	# 	'combi2'	:['#00FFD1','#00FFD1','#048000'],#blue2 
	# 	'combi3'	:['#FFFFFF','#BEBEBE','#FF0000'],#white
	# 	'combi4'	:['#0066FF','#8FBCFF','#FFFFFF'],#blue
	# 	'combi5'	:['#048000','#5A8C59','#F6A1F6'],#green2 
	# 	'combi6'	:['#01FE2A','#A9FFB7','#0066FF'],#green
	# 	'combi7'	:['#F3FF00','#FBFF9A','#01FE2A'],#yellow
	# 	'combi8'	:['#F6A1F6','#FF8CEA','#FFA200'],#pink 
	# 	'combi9'	:['#D0FF86','#F6A1F6','#00FFD1'],#green3  
	# }

	dic_colors2={
		'combi0'	:['#01FE2A','#A9FFB7','#0066FF'],#green 
		'combi1'	:['#FF00D1','#FF8CEA','#FFA200'],#pink 
		'combi2'	:['#FF0000','#FF8484','#F3FF00'],#red
		'combi3'	:['#FF0000','#FF8484','#F3FF00'],#red# :['#FFFFFF','#BEBEBE','#FF0000'],#white
		'combi4'	:['#0066FF','#8FBCFF','#FFFFFF'],#blue
		'combi5'	:['#048000','#5A8C59','#FF00D1'],#green2 
		'combi6'	:['#FFD700','#FF00D1','#00FFD1'],#oro 
		'combi7'	:['#F3FF00','#FBFF9A','#01FE2A'],#yellow
		'combi8'	:['#00FFD1','#00FFD1','#048000'],#blue2
		'combi9'	:['#FFA200','#FFCD78','#9BF50A'],#orange 
	}

	colors2 = ['combi0','combi1','combi2','combi3','combi4','combi5','combi6','combi7','combi8','combi9']

	if spectrum == 99 or spectrum == 98:
		# index=hash(name)%len(colors2)

		index =int(hashlib.md5(name).hexdigest(),16)%len(colors2)
		color=colors2[index]

		color=colors2[index]


		for k,v in dic_colors2.items():
			if k == color:
				if spectrum == 99:
					c = v[0]
				else:
					c = v[1]

	else:
		# index=hash(name)%len(colors)
		index =int(hashlib.md5(name).hexdigest(),16)%len(colors)
		color=colors[index]
		color=colors[index]

		for k,v in dic_colors.items():
			if k == color:
				c = v[spectrum]
	return c

def requestPaletteColor(request_data,list_name,spectrum):
	if len(list_name)<4:
		if spectrum != 1:
			spectrum = 99
		else:
			spectrum = 98

	list_result=[]


	for name in list_name:
		is_name = False
		is_color = False



		name_complete = name
		if spectrum != 99:
			name= name.replace(request_data['int_asr_acd'],'')
			name= name.replace('CALLS','')

		color = paletteColor(name,spectrum)
		for r in list_result: # check if the name already exits
			if r[1] == name:

				list_result.append((name_complete,name,r[2]))
				is_name = True
				break;
		if is_name == False:  #check if color exits for this name
			for r in list_result:
				if r[2] == color:
					is_color = True
	
			if is_color == False:  # if color not exist and name not exist
				list_result.append((name_complete,name,color))

			if is_color == True:

				i = 1
				new_color = paletteColor(name*i,spectrum)
				while True:
					i=i+1
					new_color = paletteColor(name*i,spectrum)
					if color != new_color:
						break
				list_result.append((name_complete,name,new_color))

	return list_result


def get_series(v_name,v_type,v_yAxis,v_data,v_color=[]):
	series = []
	try:
		for i in range(len(v_name)-1,-1,-1):
			serie = {}
			serie['type'] = v_type[i]
			serie['name'] = v_name[i].replace('All','All') #'nombre {0} a'.format(i)
			serie['yAxis'] = v_yAxis[i]

			if len(v_color)==0:
				serie['color'] = palette_color(v_name[i])   #c[v_yAxis[i]][i]
			else:
				serie['color'] = v_color[i]

			serie['data'] = v_data[i]
			series.append(serie)
	except Exception,e:
		swslog('error','list index out of range',e)
	return series

def get_yAxis(v_name,v_namedata):
	yAxis = []
	for i in range(0,len(v_name)):
		yAxi={}
		yAxi['name'] = v_name[i]
		yAxi['nameData'] = v_namedata[i]
		yAxis.append(yAxi)
	return yAxis


def highchartsCube(json_data,dif_date,request_data):
	json_data_dict = ujson.dumps(json_data)
	data = json_data_dict['rows']
	v_name_y = []
	v_asr=[]
	v_calls=[]
	v_cdrfint=[]

	for i in data:
		if dif_date=='fecha':
			v_cdrfint.append(int(i['cdrfint']))
			v_name_y.append(str(i[request_data['button']]))
		else:
			v_name_y.append(str(i['timedimension']))
			if request_data['button'] != 'ALL':
				v_cdrfint.append(int(i[request_data['button']]))

			if request_data['button'] == 'ALL':
				v_cdrfint.append('ALL-')


		val=float(i[request_data['int_asr_acd'].lower()])
		val = int(val)
		v_asr.append(val)

		val=float(i['calls'])
		val = int(val)
		v_calls.append(val)

	v_xAxis= sorted(set(v_name_y))

	d = {}
	act_elem = None
	new_v_cdrfint = {}
	n=0
	for i in range(0,len(v_cdrfint)+1):
		if i == len(v_cdrfint):
			d[act_elem]=n
			break
		if act_elem == None or act_elem != v_cdrfint[i]:
			if act_elem != None:
				d[act_elem]=n
			act_elem = v_cdrfint[i]
			new_v_cdrfint[act_elem]={request_data['int_asr_acd'].lower():[],'calls':[]}
			n = 0
		new_v_cdrfint[act_elem][request_data['int_asr_acd'].lower()].append(v_asr[i])
		new_v_cdrfint[act_elem]['calls'].append(v_calls[i])
		n+=1    
	max_elem=0
	for i in d.values():
		if i > max_elem:
			max_elem = i

	for elem,num_elem in d.items():
		while num_elem < max_elem:
			new_v_cdrfint[elem][request_data['int_asr_acd'].lower()].append(0)
			new_v_cdrfint[elem]['calls'].append(0)
			num_elem+=1

	v_name=[]
	v_data=[]
	v_type=[]
	v_yAxis=[]
	for k,v in new_v_cdrfint.items():
		for f,g in v.items():
			v_name.append('{0}{1}'.format(k,f.upper()))
			if f == request_data['int_asr_acd'].lower():
				v_type.append('column')
				v_yAxis.append(0)
			else:
				v_type.append('spline')
				v_yAxis.append(1)
			v_data.append(g)



	dict_higcharts={
		'v_xAxis':v_xAxis,
		'v_name':v_name,
		'v_type':v_type,
		'v_yAxis':v_yAxis,
		'v_data':v_data
	}
	return dict_higcharts



def adjustementDatetime(dict_higcharts,request_data):
	dict_higcharts['v_xAxis']= adjustementeDatePrevious(dict_higcharts['v_xAxis'],request_data) 
	dict_higcharts['v_xAxis'] = adjustementDateEpoch(dict_higcharts['v_xAxis'],request_data)
	return dict_higcharts

def adjustementDateEpoch(date,request_data):

	if type(date)is list:
		date_epoch = []

		# try:
		# 	TZ = (int(request_data['user_tz'][7:])*-1)-1
		# except:
		# 	TZ = -1

		dif_date = int(formatDateCube(request_data ['to_Date'])) - int(formatDateCube(request_data ['from_Date']))

		# check dif date

		if len(date)>0:
			date_begin = datetime(date[0][0],date[0][1],date[0][2],date[0][3],date[0][4],date[0][5])
			value = time.mktime(date[0])
			d_a=time.localtime(value)
			date_after = datetime(d_a.tm_year,d_a.tm_mon,d_a.tm_mday,d_a.tm_hour,d_a.tm_min,d_a.tm_sec)

			dif =  str(date_after - date_begin)
			dif = int(dif[0])



		for d in date:
			d = datetime(d[0],d[1],d[2],d[3],d[4],d[5])
			d = d - timedelta(hours=dif)
			d = formatDateCube(d)
			d = dateToArray(d)

			value = time.mktime(d)
			# if dif_date == 235900: # only for today or yesterday with 
			# 	value = value - TZ*(3600)

			date_epoch.append(value)
		return date_epoch

	if type(date)is str:
		fecha_array=dateToArray(date)
		value = time.mktime(fecha_array)
		return value

def adjustementeDatePrevious(date,request_data):
	date_new = []

	for i in date:
		if request_data['int_previous'] == 1:
			year = i[0:4]
			month = i[5:7]
			day = i[8:10]
			if day == '':
				day = 0

			hour = i[11:13]
			if hour == '':
				hour = 0

			minute = i[14:16]
			if minute == '':
				minute = 0				

			try: 
				fecha_datetime = datetime(int(year),int(month),int(day),int(hour),int(minute),00)
				fecha_datetime = fecha_datetime + request_data['dif_date']

				fecha = formatDateCube(fecha_datetime)


			except Exception, e:
				swslog('error','Month witch diferent numbers day',e)

		else:
			fecha = formatDateCube(i)

		try:
			fecha_array=[]
			fecha_array.append(int(fecha[0:4]))
			fecha_array.append(int(fecha[4:6]))
			fecha_array.append(int(fecha[6:8]))
			fecha_array.append(int(fecha[8:10]))	
			fecha_array.append(int(fecha[10:12]))
			fecha_array.append(int(fecha[12:14]))
			fecha_array.append(0)
			fecha_array.append(0)
			fecha_array.append(0)

			date_new.append(fecha_array)
		except Exception, e:
			swslog('error','month wicth diferent numbers day',e)

	return date_new


def requestSeriesHighcharts(dict_higcharts,list_color):
	series = []
	data_date = []
	try:
		for i in range(0,len(dict_higcharts['v_name'])):
			v_data_date=[]

			for j in range(0,len(dict_higcharts['v_xAxis'])):
				try:
					v_data_date.append([dict_higcharts['v_xAxis'][j] * 1000,dict_higcharts['v_data'][i][j]])	
				except Exception, e:
					swslog('error','List index out of range',e)
			data_date.append(v_data_date)		

			new_name = dict_higcharts['v_name'][i].replace('All','All')
			new_name = new_name.replace('ASR',' ASR')
			new_name = new_name.replace('ACD',' ACD')
			new_name = new_name.replace('CALLS',' CALLS')
			new_name = new_name.replace('MINUTES','MINUTES')

		
			dic_serie = {

				'color' : list_color[i][2],
				'data' : v_data_date,
				'name' : new_name,
				'yAxis': dict_higcharts['v_yAxis'][i],
				'type':dict_higcharts['v_type'][i],
			}
			series.append(dic_serie)
	except Exception, e:
		swslog('error','list index out of range',e)
	return series

def requestDateHighcharts(dict_higcharts):
	data_date = []
	for i in range(0,len(dict_higcharts['v_name'])):

		v_data_date=[]

		for j in range(0,len(dict_higcharts['v_data'][i])):
			v_data_date.append([dict_higcharts['v_xAxis'][j] * 1000,dict_higcharts['v_data'][i][j]])	

		data_date.append(v_data_date)		

	return data_date



def intervalAdjustment(dict_higcharts,adjustment_factor,request_data):

	v_date = []


	for i in range(0,len(dict_higcharts['v_xAxis'])):
		if int(math.fmod(int(i),adjustment_factor))==0:
			v_date.append(dict_higcharts['v_xAxis'][i])
	dict_higcharts['v_xAxis']=v_date
	name = []

	for i in dict_higcharts:
		name.append(i)

	v_data_new = []
	v_vect_new = []
	v_xAxis_new = []

	total = 0
	c=0
	dict_higcharts_new={}
	for n in name:
		for dic in dict_higcharts[n]:
			if n == 'v_data':
				men_total = 0
				cont = 0
				for data in dic:
					if cont < adjustment_factor-1:
						cont = cont + 1 
						men_total = men_total + data
					else:
						# v_data_new.append(men_total/adjustment_factor);
						v_data_new.append(men_total);
						men_total = 0
						cont = 0	
				v_vect_new.append(v_data_new)
				v_data_new = []

			if n == 'v_xAxis':
				 v_xAxis_new.append(dic)

		if n == 'v_data':
			dict_higcharts_new[n] = v_vect_new
		elif n == 'v_xAxis':
			dict_higcharts_new[n] = v_xAxis_new
		else:
			dict_higcharts_new[n] = dict_higcharts[n]

	return dict_higcharts_new


def higchartsTitle(dict_higcharts):
	len_xAxis = len(dict_higcharts['v_xAxis'])

	pattern = dict_higcharts['v_xAxis'][0]
	pattern_new = ''

	for dic in dict_higcharts['v_xAxis']:
		for i in range(0,len(dic)):
			if dic[i] == pattern[i]:
				pattern_new = pattern_new + dic[i]
			if dic[i] != pattern[i]:
				pattern_new = pattern_new + '0'
		pattern= pattern_new
		pattern_new = ''

	pattern = pattern[:-6]
	return pattern


def getEpochDatatime(request_data):
	if request_data['min_Epoch'] != 'NULL':
		from_epoch = int(float(str(request_data['min_Epoch'])))
		from_epoch = from_epoch/1000
		request_data['from_Date']= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(from_epoch))
	if request_data['max_Epoch'] != 'NULL':
		to_epoch = int(float(str(request_data['max_Epoch'])))
		to_epoch = to_epoch/1000
		request_data['to_Date']= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(to_epoch))

def get_chart_time(value):
	# Historical channel usage
	if type(value) is str:
		return (time.mktime(datetime.strptime(value, "%Y-%m-%d %H:%M:%S")))*1000
	elif type(value) is datetime:
		return time.mktime(value.timetuple())*1000
	else:
		raise TypeError('Type not recognized')

def get_chart_time_new(value):
	# Historical channel usage
	if type(value) is str:
		value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
	if type(value) is datetime:
		fecha_array=[]
		fecha_array.append(value.year)
		fecha_array.append(value.month)
		fecha_array.append(value.day)
		fecha_array.append(value.hour)
		fecha_array.append(value.minute)
		fecha_array.append(value.second)
		fecha_array.append(0)
		fecha_array.append(0)
		fecha_array.append(0)
		return time.mktime(fecha_array)
	else:
		raise TypeError('Type not recognized')

def toMuchDataControl(request_data,dict_response):
	to_much_data = False
	total_data = 0
	num_column = 0
	num_data = 0
	for i in dict_response['series']:
		num_data = len(i['data'])
		num_column = num_column + 1
		total_data = total_data + len(i['data'])

	if num_column > 75:
		dict_response['title']='Too much data'
		dict_response['series']=""

	elif num_column > 60 and num_data > 1:
		to_much_data = True			

	elif num_column > 50 and num_data > 2:
		to_much_data = True		

	elif num_column > 40 and num_data > 4:
		to_much_data = True	

	elif num_column > 30 and num_data > 8:
		to_much_data = True	

	elif num_column > 20 and num_data > 16:
		to_much_data = True	
	elif num_column > 10 and num_data > 150:
		to_much_data = True	

	elif num_column * num_data > 2000:
		to_much_data = True


	if to_much_data == True:
		request_data['agrupation_data'] = int(request_data['agrupation_data']) +1
		request_data['agrupation_data'] = str(request_data['agrupation_data'])

	return to_much_data

