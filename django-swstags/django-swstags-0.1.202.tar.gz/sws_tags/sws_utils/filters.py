#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
'''
filters.py

Filtering utility library

Created by SWS on 2012-09-11.
Copyright (c) 2012 StoneWorkSolutions. All rights reserved.
'''
from datetime import datetime,date,timedelta
from django.utils.translation import ugettext_lazy as _ # Internacionalization
from math import ceil
import time
from sws_tags.sws_utils.common_utils import *
import re
from decimal import *
import types
from types import *
import time
from django.utils.datastructures import SortedDict

from sws_tags.sws_utils import json_encode
from sws_tags.sws_utils.cube import numberFormatter
####################################################################################################

##############################################################
## Filtering function
###################################################
## queryset:  Set of data to filter: Number.objects.all()
## filters: List of key value pairs of the filters to create: [(client, client__client),(destination, destination__destination)]
## set_filters: Set of filters received from the template, requst.GET { client:5,destination:7}
## firstLoad: The first is False after True because the data is JSON
## from_date_days: Number of days between from and to
## return_filters: True if return filters
#################################################################

def createFilter(queryset,filters,firstLoad=False,days_between_calendars=0,time=19,filter_by_date=True,request_data = False):
	new_filters = SortedDict()
	for filter in filters:
		if filter[1] == 'date_range'and filter_by_date:
			date_fields = ["from_"+filter[1],"to_"+filter[1]]


			if request_data == False:
				if time > 12:
					now = datetime.datetime.now()
					from_date = now.today() - timedelta(hours=now.hour,minutes=now.minute,seconds=now.second)
					from_date = from_date.strftime("%Y-%m-%d %H:%M:%S") 
					to_date = now.today() - timedelta(hours=now.hour,minutes=now.minute,seconds=now.second) + timedelta(hours=23,minutes=59,seconds=59)
					to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")
				else:
					from_date = date(date.today().year,date.today().month,date.today().day)
					to_date = from_date + timedelta(days=1)
			else:
				if time > 12:
					now = datetime.datetime.now()
					# from_date = now.today() - timedelta(hours=now.hour,minutes=now.minute,seconds=now.second)
					# from_date = from_date.strftime("%Y-%m-%d %H:%M:%S") 
					# to_date = now.today() - timedelta(hours=now.hour,minutes=now.minute,seconds=now.second) + timedelta(hours=23,minutes=59,seconds=59)
					# to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")
					from_date = request_data['from_Date']
					to_date = request_data['to_Date']
					from_date = from_date.strftime("%Y-%m-%d %H:%M:%S") 
					to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")
				else:
					# from_date = date(date.today().year,date.today().month,date.today().day)
					# to_date = from_date + timedelta(days=1)

					from_date = request_data['from_Date']
					to_date = request_data['to_Date']
					from_date = from_date.strftime("%Y-%m-%d %H:%M:%S") 
					to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")

			
			new_filters[filter[0]] = {	   'label':  getFieldVerboseName(queryset,filter[0]),
										   'values':[from_date,to_date],
										   'date_range':True
										  }
		else:
			if filter[1] == 'date_picker':

				date_fields = ["from_"+filter[1],"to_"+filter[1]]
				if request_data == False:
					if time > 12:
						now = datetime.datetime.now()
						# formating from date and to date
						# from_date = now.today() - timedelta(days=days_between_calendars)
						from_date = now.today() - timedelta(hours=now.hour,minutes=now.minute)
						# from_date = request_data['from_Date']

						from_date = from_date.strftime("%Y-%m-%d %H:%M") 
						# to_date = now.strftime("%Y-%m-%d %H:%m")
					else:
						# now = datetime.now()
						# # formating from date and to date
						# # from_date = now.today() - timedelta(days=days_between_calendars)
						# from_date = now.today() 
						
						# # to_date = now.strftime("%Y-%m-%d %H:%m")
						# to_date = now.today() - timedelta(days=1)
						from_date = date(date.today().year,date.today().month,date.today().day)
						# from_date = request_data['from_Date']
						from_date = from_date.strftime("%Y-%m-%d %H:%M:%S") 
						# from_date = from_date.strftime("%Y-%m-%d") 
						# to_date = to_date.strftime("%Y-%m-%d")
				else:
					from_date = request_data['from_Date']

					from_date = from_date.strftime("%Y-%m-%d %H:%M:%S") 
				
				new_filters[filter[0]] = {	   'label':  getFieldVerboseName(queryset,filter[0]),
											   'values':[from_date],
											   'date_picker':True
											  }

			else:

				#create new_filters 
				if firstLoad:
					if type(queryset) == list:
						new_filters[filter[0]] = {
								'label':  getFieldVerboseName(queryset,filter[1]),
								'values': sorted(set([(q[filter[0]],q[filter[1]]) for q in queryset]),key=lambda q: q[1]),
								'default':filter[2],
						}
					else:
					# print "Filter query:",(queryset.values_list(filter[0],filter[1]).distinct().order_by(filter[1])).query
						new_filters[filter[0]] = {
											'label':  getFieldVerboseName(queryset,filter[0]),
											# converted from querysetvalueslist to list to be able to modify content values if boolean, it shouldn't affect other filters
											'values': list(queryset.values_list(filter[0],filter[1]).distinct().order_by(filter[1])),
											'default':filter[2],
										}	
				else:	
					if type(queryset) == list:
						new_filters[filter[0]] = sorted(set([(q[filter[0]],q[filter[1]]) for q in queryset]),key=lambda q: q[1])
					else:
						# converted from querysetvalueslist to list to be able to modify content values if boolean, it shouldn't affect other filters
						new_filters[filter[0]] = list(queryset.values_list(filter[0],filter[1]).distinct().order_by(filter[1]))
						
	if firstLoad:
		for k,v in new_filters.items():
			if 'date_range' not in v and 'date_picker' not in v:
				for i in range(0,len(v['values'])):
					if type(v['values'][i][0]) == bool:
						# if k in bool_filters
						new_filters[k]['values'][i] = (1 if v['values'][i][0] else 0,v['values'][i][1])
	else:
		for k,v in new_filters.items():
			if 'date_range' not in v and 'date_picker' not in v:
				for i in range(0,len(v)):
					if type(v[i][0]) == bool:
						new_filters[k][i] = (1 if v[i][0] else 0,v[i][1])
	return new_filters



def filterData(queryset,filters,set_filters,filter_by_date=True):
	# print 'set_filters =',set_filters
	# If set_filters is received, filter the received data. Most commonly this is request.GET
	# t0 = time.time() 

	clean_filters = {}
	if len(set_filters.items()) > 0:
	# Create a clean dictionary of key:value pairs to filter
		for filter in filters:
			# Check for date field
			if filter[1] == 'date_range' and filter_by_date:
				# Filter by date range
				date_fields = ["from_"+filter[0],"to_"+filter[0]]
				date_range = filter[0] + '__range'
				# for s in set_filters:
					# if s.find(date_fields[0]) != -1 and set_filters[s] not in ('',None,'None'):
				if date_fields[0] in set_filters and set_filters[date_fields[0]] not in ('',None,'None'):
						# print 'type(s)=',type(s)
						# clean_filters[date_range] = [set_filters[s] , set_filters[s.replace('from','to')]]
						clean_filters[date_range] = [set_filters[date_fields[0]] , set_filters[date_fields[1]]]
						# print 'clean_filters =',clean_filters

			else:
				if filter[0] in set_filters and set_filters[filter[0]] not in ('',None,'None'):
					clean_filters[filter[0]] = set_filters[filter[0]]

	# print 'clean_filters={0}'.format(clean_filters)
	# print 'query={0}'.format(queryset)
	

	queryset = queryset.filter(**clean_filters)
	# print 'query={0}'.format(queryset)

	# t1 = time.time()

	# print 'IT TOOK {0} secs to filter the query'.format((t1-t0))
	
	return queryset





def filterDataUTC(queryset,filters,set_filters,filter_by_date=True):
	request_data

	clean_filters = {}
	if len(set_filters.items()) > 0:
		for filter in filters:
			if filter[1] == 'date_range' and filter_by_date:
				date_fields = ["from_"+filter[0],"to_"+filter[0]]
				date_range = filter[0] + '__range'
				if date_fields[0] in set_filters and set_filters[date_fields[0]] not in ('',None,'None'):
						clean_filters[date_range] = [set_filters[date_fields[0]] , set_filters[date_fields[1]]]
			else:
				if filter[0] in set_filters and set_filters[filter[0]] not in ('',None,'None'):
					clean_filters[filter[0]] = set_filters[filter[0]]
	queryset = queryset.filter(**clean_filters)	
	return queryset





def orderData(queryset, request,view_name=None):
	if request['sord'] == 'asc':
		name_order = request['sidx']
	else:
		name_order = '-'+request['sidx']

	# if type(name_order)== str:
	if view_name!= None:
		name_order=name_order.replace(view_name+'_table_grid_','')
	# print 'QUERY = {0}'.format(queryset)
	t0 = time.time()
	queryset = queryset.order_by(name_order)
	t1 = time.time()
	# print 'IT TOOK {0} secs to order the query'.format((t1-t0))
	# print 'QUERY = {0}'.format(queryset)


# b = a[a.index('_')+1:]
	return queryset

def orderList(list,request, view_name=None,regex=None):

	if request['sord'] == 'asc':
		rev = False
	else:
		rev = True

	name_order = request['sidx']
	
	if view_name!= None:
		name_order=name_order.replace(view_name+'_table_grid_','')

	if regex is None:
		return sorted(list, key = lambda a: a[name_order],reverse = rev)

	# Use a replacement regex for the key
	else:
		c_regex = re.compile(regex)
		return sorted(list, key = lambda a: re.sub(c_regex,'',a[name_order]),reverse = rev)


def gridData(queryset, request,footerData='false'):
	import time
	# Total number of rows
	if type(queryset) == list:
		records = len(queryset)
	else:
		records = queryset.count()

	rows = int(request['rows'])
	# Rows to return
	total = int(ceil(float(records)/float(rows)))

	# Page to return
	page = int(request['page'])

	# Subset of rows
	from_row = ((page*rows)-rows)

	to_row = (page*rows)

	if to_row > records:
		to_row = records

	rows = queryset[from_row : to_row]

	# for i in range(0,len(rows)):
	# 	if 'cost' in rows[0]:
	# 		rows[i]['cost'] = str(rows[i]['cost'])+ ' €'

	# 	if 'income' in rows[0]:
	# 		rows[i]['income'] = str(rows[i]['income'])+ ' €'

	# 	if 'usd_cost' in rows[0]:
	# 		rows[i]['usd_cost'] = str(rows[i]['usd_cost'])+ ' $'

	# 	if 'usd_income' in rows[0]:
	# 		rows[i]['usd_income'] = str(rows[i][usd_'income'])+ ' $'


	if footerData != 'false':
		return json_encode({
								'total': total,
								'records': records,
								'page': page,
								'rows': rows,                   
								'footerData': footerData,
								})
	else:
		return json_encode({
						'total': total,
						'records': records,
						'page': page,
						'rows': rows,                   
						})



def totalQueryset(queryset):
	field_aggregate = queryset.aggregate_names

	# print 'aquiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii',field_aggregate



	queryset_total = queryset.values(*field_aggregate)
	new_queryset_total = {}
	# print queryset_total
	for i in queryset_total:
		for k,v in i.items():
			
			# We modify this if line because we weren't taking care of so many other types that should not be taken care of such as:
			# str, unicode, bool etc....
			# if type(v) is not NoneType and type(v) is not datetime:
			if not isinstance(v,NoneType) and not isinstance(v,datetime.datetime) and not isinstance(v,str) and not isinstance(v,bool) and not isinstance(v,unicode):
				if k not in new_queryset_total:
					new_queryset_total[k] = v
				else:
					new_queryset_total[k] += v

	for n in new_queryset_total:
		new_queryset_total[n] = numberFormatter(new_queryset_total[n])
	# for k,v in new_queryset_total.items():
	# 	# if isinstance(v,Decimal):
	# 	new_queryset_total[k]=round(float(v),2)

	return new_queryset_total



def gridDataList(listData, request):
	
	records = len(listData)

	rows = int(request['rows'])
	page = int(request['page'])

	total = int(ceil(float(records)/float(rows)))

	from_row = ((page*rows)-rows)

	to_row = (page*rows)

	if to_row > records:
		to_row = records

	rows = listData[from_row : to_row]

	return json_encode({
							'total': total,
							'records': records,
							'page': page,
							'rows': rows                   
							})

def StrictFilterData(queryset, filters, set_filters,firstLoad=False,from_date_days = 1, return_filters = True):
	new_filters = {}
	filter_names = {}

	# If set_filters is received, filter the received data. Most commonly this is request.GET
	if len(set_filters.items()) > 0:
		# Create a clean dictionary of key:value pairs to filter
		clean_filters = {}
		for filter in filters:
			# Check for date field
			if filter[1] == 'date_range':
				# Filter by date range
				date_fields = ["from_"+filter[0],"to_"+filter[0]]
				date__range = filter[0] + '__range'

				if date_fields[0] in set_filters and set_filters[date_fields[0]] not in ('',None,'None'):
					clean_filters[date__range] = [set_filters[date_fields[0]] , set_filters[date_fields[1]]]

			else:
				if filter[0] in set_filters and set_filters[filter[0]] not in ('',None,'None'):
					clean_filters[filter[0]] = set_filters[filter[0]]

		# print "Clean filters" + str(clean_filters)
		# Filter the data unpacking the clean dictionary into key value pairs (kwargs like) 
		#print "Clean filters",clean_filters
		# print "Items before filtering {0}".format(queryset.count())
	
		queryset = queryset.filter(**clean_filters)
		# -name_colum   ->order descending , name_colum   -> order ascending	

		name = set_filters.get("name")
		sortorder = set_filters.get("sortorder")
		if sortorder == 'asc':
			name_order = str(name)
		else:
			name_order = '-'+str(name)
		queryset = queryset.order_by(name_order)

		#queryset = queryset.filter(validity_date__range=['2010-01-01','2010-12-31'])
		#print "Items after filtering {0}".format(queryset.count())

	# once the data is filtered, create the new filters

	# Create the filters values
	for filter in filters:
		#print "Creating filter {0}".format(filter)
		if filter[1] == 'date_range':
			date_fields = ["from_"+filter[1],"to_"+filter[1]]

			now = datetime.datetime.now()
			# formating from date and to date
			from_date = now.today() - timedelta(days=from_date_days)
			from_date = from_date.strftime("%Y-%m-%d")
			to_date = now.strftime("%Y-%m-%d")

			new_filters[filter[0]] = { 'label':  _(filter[0].capitalize()),
																	   #'values': {'from_date':from_date,'to_date':to_date},
																	   'values':[from_date,to_date],
																	   'date_range':True
																	  }
		else:
			#create new_filters
			if firstLoad:
					new_filters[filter[0]] = queryset.values_list(filter[0],filter[1]).distinct().order_by(filter[1])
			else:
					new_filters[filter[0]] = {
																	'label': _(filter[0].capitalize()),
																	'values': queryset.values_list(filter[0],filter[1]).distinct().order_by(filter[1])
															}
	return queryset, new_filters



def updateGridToVal(field_query_detail,col_cube,request_data,model,filters):
	if type(field_query_detail) == list:
		field = []
		for i in field_query_detail:
			field.append(i[0])
		field_query_detail = field
	
	
	detail_filters = {}
	new_date = {}
	if request_data['val1'] !='NULL' or request_data['val2'] !='NULL':
	
		if request_data['val1']!='NULL':
			index_group_by = 'Date'
			for col in col_cube:
				if col[0] == request_data['group_by']: 
	
					index_group_by = col[3]

			if index_group_by == 'Date':
				new_date[request_data['group_by']] = request_data['val1']
			else:	
				detail_filters[index_group_by] = request_data['val1']
		if request_data['val2']!='NULL':
			index_and_by = 'Date'
			for col in col_cube:
				if col[0] == request_data['and_by']: 
	
					index_and_by = col[3]
			if index_and_by == 'Date':
				new_date[request_data['and_by']] = request_data['val2']
			else:

				detail_filters[index_and_by] = request_data['val2']
		
	
		if new_date:
			year_from = str(request_data['from_Date'])[0:4]
			year_to = str(request_data['to_Date'])[0:4]

			month_from = str(request_data['from_Date'])[5:7]
			month_to = str(request_data['to_Date'])[5:7]

			day_from = str(request_data['from_Date'])[8:10]
			day_to = str(request_data['to_Date'])[8:10]
			
			hour_from = str(request_data['from_Date'])[11:13]
			hour_to = str(request_data['to_Date'])[11:13]
			
			minute_from = str(request_data['from_Date'])[14:16]
			minute_to = str(request_data['to_Date'])[14:16]

			second_from = str(request_data['from_Date'])[17:19]
			second_to = str(request_data['to_Date'])[17:19]
			

			if ('Month Field' in new_date):
				month_from = str(new_date['Month Field'])
				month_to = str(new_date['Month Field'])

				

				if (month_from!=str(request_data['from_Date'])[5:7]):
					day_from = str(1)
					hour_from = str(00)
					minute_from = str(00)
					second_from = str(00)

				if (month_to!=str(request_data['to_Date'])[5:7]):
					day_to = str(last_day_of_month(year_from,month_from))
					hour_to = str(23)
					minute_to = str(59)
					second_to = str(59)

			if ('Day Field' in new_date):
				
				day_from = str(new_date['Day Field'])
				day_to = str(new_date['Day Field'])
				
				
				if (new_date['Day Field']!=str(request_data['from_Date'])[8:10]):
					hour_from = str(0)
					minute_from = str(0)
					second_from = str(0)
				
				if (new_date['Day Field']!=str(request_data['to_Date'])[8:10]):
					
					hour_to = str(23)
					minute_to = str(59)
					second_to = str(59)

				
				if (new_date['Day Field']==str(request_data['from_Date'])[8:10]):
					hour_from = str(request_data['from_Date'])[11:13]
					minute_from = str(request_data['from_Date'])[14:16]
					second_from = str(request_data['from_Date'])[17:19]
				
				if (new_date['Day Field']==str(request_data['to_Date'])[8:10]):
					
					hour_to = str(request_data['to_Date'])[11:13]
					minute_to = str(request_data['to_Date'])[14:16]
					second_to = str(request_data['to_Date'])[17:19]

			

			user_tz = request_data['django_timezone'] 
			from_Date = datetime.datetime(int(year_from),int(month_from),int(day_from),int(hour_from),int(minute_from),int(second_from),tzinfo=user_tz)
			to_Date = datetime.datetime(int(year_to),int(month_to),int(day_to),int(hour_to),int(minute_to),int(second_to),tzinfo=user_tz)
			request_data['from_Date']=from_Date
			request_data['to_Date']=to_Date




		
		if len(detail_filters)==2: # two fields

			queryset_detail = model.objects.filter(**detail_filters)
			queryset_detail = queryset_detail.filter(calldate__range=[request_data['from_Date'],request_data['to_Date']])
			queryset_detail =excludeFilters(request_data,filters,col_cube,queryset_detail)
		elif len(detail_filters) ==1: #one field and one date

			queryset_detail = model.objects.filter(**detail_filters)
			queryset_detail = queryset_detail.filter(calldate__range=[request_data['from_Date'],request_data['to_Date']])
			queryset_detail =excludeFilters(request_data,filters,col_cube,queryset_detail)
			
		else: #two date

			queryset_detail = model.objects.filter(calldate__range=[request_data['from_Date'],request_data['to_Date']])
			queryset_detail =excludeFilters(request_data,filters,col_cube,queryset_detail)
	else: # only first load
		


		queryset_detail = model.objects.filter(calldate__range=[request_data['from_Date'],request_data['to_Date']])[:5]
		
	
	
	

	queryset_detail=queryset_detail.values(*field_query_detail)
	return queryset_detail


def last_day_of_month(year, month):
        """ Work out the last day of the month """
        year=int(year)
        month=int(month)
        last_days = [31, 30, 29, 28, 27]
        for i in last_days:
                try:
                        end = datetime.datetime(year, month, i)
                except ValueError:
                        continue
                else:
                        return end.day
        return None

def excludeFilters(request_data,filters,col_cube,queryset_detail):
	
	filtros_selec={}
	for i in filters:
		# print i[0][0]
		if i[0][0] in request_data:
			
			if ((request_data[i[0][0]]!= 'NULL')):

				filtros_selec[i[0][0]]=request_data[i[0][0]]

	if (filtros_selec):
		queryset_detail=excludeWithFilter(filtros_selec,queryset_detail,col_cube)
	
	return queryset_detail

def excludeWithFilter(filtros_selec,queryset_detail,col_cube):
	filtros_buenos={}
	for i in filtros_selec: 
		for j in col_cube:
			if i==j[0]:
				filtros_buenos[j[4]]=filtros_selec[i]
	
	queryset_detail=queryset_detail.filter(**filtros_buenos)

		

	return queryset_detail


def cleanEmptyFilters(new_filters,first_load):
	for k,v in new_filters.items():
		if first_load:
			v['values'] = [valor for valor in v['values'] if valor != (None,None)]
		else:
			new_filters[k] = [valor for valor in v if valor != (None,None)]
	return new_filters



def dictFilters(dimension_filters):
	dimension_filters = dict((d[2],d[0]) for d in dimension_filters)  #dimension_filters = dict((d[0],(d[1],d[2])) for d in dim
	
	if 'Icx' in dimension_filters:	
		del dimension_filters['Icx']
		dimension_filters['Icx In'] = 'Outboundinterconnection'
		dimension_filters['Icx Out'] = 'Inboundinterconnection'
	return dimension_filters
