#!/usr/bin/env python
# encoding: utf-8
"""
Created by Miguel A. Sanchez on 2012-10-05.
Copyright (c) 2010 StoneWorkSolutions. All rights reserved.
"""
import django.db.models
from django.contrib.sites.models import Site
from django import template
from django.utils.translation import ugettext_lazy as _
from sws_tags.sws_utils.highcharts import *
import time
import logging
from decimal import Decimal
from sws_tags.sws_utils.common_utils import *

logger = logging.getLogger('django')

register = template.Library()

ROWS_TO_EVALUATE = 25


##############################################################################################################
############################################--TAG FILTERS--###################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_filters.html')
def tag_filters(view_name,
				filters,
				shortcuts='false',
				vertical='false',
				shortcuts_select='today'
				):  
	"""
	  **Description:**
		This tags create a serie of select.
	  
	  **Request:**
		>>> {% tag_filters 'VP' filters shortcuts 'false' 'today' %}
		
	  **Param:**
		#. 'VP' -> view name
		#. 'filters'-> list with filters
		#. 'shortcuts' or 'false' -> list with shorcuts or false if not shortcuts
		#. 'false' or 'true'-> false for normal case or true for filters in vertical
		#. 'today'-> default shortcuts for first load

	  **Event:** 
		>>> case 'filters': #when click on filters
		>>> case 'b_clear': #when click on button clear
		>>> case 'shortcuts': #when click on shortcuts
  
	  **Import:**
		>>> none

	  .. note:: 
		none
	"""

	date_field = 'False'

	for i in filters:
		# print i
		if i == 'calldate' or i == 'notification_date':
			date_field = 'True'


	return {'view_name':view_name,
			'filters': filters,
			'shortcuts':shortcuts,
			'vertical':vertical,
			'shortcuts_select':shortcuts_select,
			'date_field':date_field,
			}

##############################################################################################################
####################################--TAG FILTERS SELECT2--###################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_filters_select2.html')
def tag_filters_select2(view_name,
						dimension_filters,
						URL_FILTERS_CUVE,
						shortcuts='false',
						vertical='false',
						name='',
						shortcuts_default='today',
						format_date = 'yyyy-mm-dd HH:MM:ss'
						):
	"""
	  **Description:**
		This tags create a serie of select.
	  
	  **Request:**
		>>> {% tag_filters_select2 'VP' dimension_filters URL_FILTERS_CUBE 'false' 'true' '' 'today' %}
		
	  **Param:**
		#. 'VP' -> view name
		#. dimension_filters -> is a list of tuple with the next format:
		#. dimension_filters=[('calldate','date_range',str(unicode())),('client','shortname',str(unicode(('Client')))),]
		#. URL_FILTERS_CUBE -> url for refresh grid
		#. false -> false if not shortcuts and true if have shortcuts
		#. false -> false if vertical and true if horizontal
		#. '' -> by default '' only asign name if two or more tag_filters_select2
		#. 'today' -> today or other shorcuts, this is shortcuts select for first load 

	  **Event:** 
		>>> case 'filters': #when click on filters
		>>> case 'b_clear': #when click on button clear
		>>> case 'shortcuts': #when click on shortcuts
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""

	date_field = 'False'

	for i in dimension_filters:
		if i == 'Date':
			date_field = 'True'

	# print 'sssssssssss',date_field

	return {'view_name':view_name,
			'dimension_filters': dimension_filters,
			'URL_FILTERS_CUVE':URL_FILTERS_CUVE ,
			'shortcuts':shortcuts,
			'vertical':vertical,
			'name':name,
			'shortcuts_default':shortcuts_default,
			'date_field':date_field,
			'format_date':format_date,

			}



##############################################################################################################
####################################--TAG SHORTCUTS--###################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_shortcuts.html')
def tag_shortcuts(view_name,
				shortcuts=None,
				shortcuts_select='today'
				):

	"""
	  **Description:**
		This tags create a serie of button or select.
	  
	  **Request:**
		>>> { tag_shortcuts 'VP' shortcuts }
		
	  **Param:**
		#. 'VP' ---------> view name
		#. 'Shortcuts'---> list with filters
		#. 'today'-------> default shortcuts for first load

	  **Event:** 
		>>> case 'shortcuts': when click on shortcuts
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""


	# Shortcut translations
	shortcuts_trans = {
					'1m':           _('1 minute'),
					'5m':           _('5 minutes'),
					'10m':          _('10 minutes'),
					'20m':          _('20 minutes'),
					'30m':          _('30 minutes'),
					'1h':           _('1 hour'),
					'2h':           _('2 hours'),
					'3h':           _('3 hours'),
					'6h':           _('6 hours'),
					'12h':          _('12 hours'),
					'24h':          _('24 hours'),
					'today':        _('Today'),
					'yesterday':    _('Yesterday'),
					'week':         _('Curr. week'),
					'month':        _('Curr. month'),
					'pweek':        _('Prev. week'),
					'pmonth':       _('Prev. month'),
					'lastseven':    _('Last 7 days'),
					'lastthirty':   _('Last 30 days'),
					'year':         _('Year'),
					'all':          _('All'),

	}

	shortcuts_list = []

	# Define the order of the shortcuts
	shortcuts_order = ['1m','5m','10m','20m','30m','1h','2h','3h','6h','12h','24h', 'today','yesterday','week','lastseven','pweek','month','lastthirty','pmonth','year','all']

	if shortcuts != None:
		# Assign the translation to the received shortcuts list
		for s in shortcuts_order:
			if s in shortcuts:
				shortcuts_list.append((s,shortcuts_trans[s]))
	return {'view_name':view_name,
			'shortcuts':shortcuts_list,
			'shortcuts_select':shortcuts_select
			}

##############################################################################################################
####################################--TAG SHORTCUTS--###################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_speedometer.html')
def tag_speedometer(view_name,speedometer_name,speedometer_text,min,max,text,default_value,invert='false'):

	"""
	  **Description:**
		This aaaaa
	  
	  **Request:**
		>>> { tag_shortcuts 'VP' shortcuts }
		
	  **Param:**
		#. 'VP' ---------> view name
		#. 'Shortcuts'---> list with filters
		#. 'today'-------> default shortcuts for first load

	  **Event:** 
		>>> case 'shortcuts': when click on shortcuts
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""

	return {'view_name':view_name,
			'speedometer_name':speedometer_name,
			'speedometer_text':speedometer_text,
			'min':min,
			'max':max,
			'text':text,
			'default_value':default_value,
			'invert':invert,
			}



##############################################################################################################
####################################--TAG REFRESH TIME--######################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_refresh_time.html')
def tag_refresh_time(view_name,
					refresh_time
					):
	"""
	  **Description:**
		This tags create a counter with time and a button Refresh Time

	  **Request:**
		>>> {% tag_refresh_time 'VP' 20 %}
		
	  **Param:**
		#. 'VP' -> view name
		#. '20' -> integer witch time of refresh

	  **Event:** 
		>>> case 'shortcuts': when click on shortcuts
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	return {'view_name':view_name,
			'refresh_time':refresh_time
			}


# @register.inclusion_tag('tags/tag_utils.html')
# def tag_utils(name):
#   return {name = 'name'}


##############################################################################################################
############################################--TAG GRID--######################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_grid.html')
def tag_grid(view_name,
			queryset,
			jsonReader_id,
			sortname,
			URL_GRID,
			multiselect = 'false',
			footerrow = 'false',
			adjustment_factor=1,
			col_order='false',
			middle_col='false',
			row_num=200,
			checkboxColumn='false',
			subGrid='false',
			align = 'center',
			):
	"""
	  **Description:**
		This tags create a grid

	  **Request:**
		>>> {% tag_grid 'VP' queryset jsonReader_id sortname URL_GRID 'false' 'false' 0.8 'false' 'false' 200 checkboxColumn subGrid %}
		
	  **Param:**
		#. 'VP' --------------> view name
		#. 'queryset'---------> queryset
		#. 'jsonReader_id'----> name identification
		#. 'sortname'---------> name for order
		#. 'URL_GRID'---------> url declaration in views for refresh grid
		#. 'false'------------> false for not multiselect or true for multiselect
		#. 'false'------------> false for not footerrow or true for footerrow
		#. '0.8' -------------> adjustment factor by column (necesary middle column true)
		#. 'col_order' -------> order of columns
		#. 'false'------------> false for not middle in size column or true for middle in size column
		#. 200----------------> number of rows for the first load
		#. 'false'------------> false for not firs load
		#. 'false'------------> false if not subgrid

	  **Event:** 
		>>> case 'grid': #when click on cell
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""

	col_name=[]
	col_model=[]
	col_name,col_model = getGridConfig(queryset,adjustment_factor,col_order,middle_col,align)

	if checkboxColumn != 'false':
		col_name.append('Sel. Multiple')
		col_model.append({'width':1,'align':'center','name':'check_column', 'editable':'true', 'edittype':'checkbox', 'editoptions': { 'value':"True:False"}, 'formatter': "checkbox", 'formatoptions': {'disabled' : 'false'}})


	# print 'aaaaaaaaaaaaaaaaaa'
	# print col_model

	# col_name =  ['Client', 'Destino', 'Llamadas', 'Calls not tarified', 'Moneda', 'Total Reseller', 'Total Admin', 'Total Client', 'Total Superreseller', 'Minutos']
	# col_model = [{'width': 1, 'align': 'center', 'name': 'client__client'}, {'width': 1, 'align': 'center', 'name': 'destination__destination'},{'width': 1, 'align': 'center', 'name': 'calls'}, {'width': 1, 'align': 'center', 'name': 'non_calls'}, {'width': 1, 'align': 'center', 'name': 'admin_income_currency'}, {'width': 1, 'align': 'center', 'name': 'total_reseller_income'}, {'width': 1, 'align': 'center', 'name': 'total_admin_income'}, {'width': 1, 'align': 'center', 'name': 'total_client_income'}, {'width': 1, 'align': 'center', 'name': 'total_superreseller_income'}, {'width': 1, 'align': 'center', 'name': 'minutes'}]

	return {'view_name':view_name,
			'URL_GRID':URL_GRID,
			'col_name':col_name,
			'col_model':col_model,
			'jsonReader_id':jsonReader_id,
			'sortname':sortname,
			'multiselect':multiselect,
			'footerrow':footerrow,
			'row_num':row_num,
			'subGrid':subGrid
			}



##############################################################################################################
############################################--TAG GRID--######################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_grid_dict.html')
def tag_grid_dict(view_name,
			URL_GRID,
			conf_data,
			conf_option={},
			conf_param={},
			):

	#################### conf param default
	conf_param_default = {}
	conf_param_default['adjustment_factor'] = 1
	conf_param_default['middle_col'] = 'false'
	conf_param_default['checkboxColumn'] = 'false'


	#################### conf option default
	conf_option_default = {}
	conf_option_default['jsonReader_id'] = 'None'
	conf_option_default['multiselect'] = 'false'
	conf_option_default['footerrow'] = 'false'
	conf_option_default['row_num'] = 200
	conf_option_default['subGrid']= 'false'
	conf_option_default['align'] = 'false'
	conf_option_default['sortname'] = 'NULL'
	conf_option_default['autowidth'] = 'true'
	conf_option_default['shrinkToFit'] = 'false'
	conf_option_default['scroll'] = 1
	conf_option_default['cm_sortable'] = 'true'

	conf_param = updateDict(conf_param_default,conf_param)

	conf_option = updateDict(conf_option_default,conf_option)


	col_name=[]
	col_model=[]

	if type(conf_data) == list:
		if len(conf_data[0]) > 3:
			dic_col_model = []
			col_len = []
			col_align = []
			for i in conf_data:
				col_name.append(str(unicode(i[0])))
				col_model.append(i[1])
				col_len.append(i[2])
				col_align.append(i[3])

			try:
				for i in range(0,len(col_model)):
					dic_col_model.append({'name':col_model[i],
										'width':col_len[i],
										'align':col_align[i],
										})
			except:
				logger.error('getGridConfig: error in asignation len a column of grid')

		col_model = dic_col_model

	if conf_param_default['checkboxColumn'] != 'false':
		col_name.append('Select multiple')
		col_model.append({'width':1,'align':'center','name':'check_column', 'editable':'true', 'edittype':'checkbox', 'editoptions': { 'value':"True:False"}, 'formatter': "checkbox", 'formatoptions': {'disabled' : 'false'}})

	# col_name =  ['Client', 'Destino', 'Llamadas', 'Calls not tarified', 'Moneda', 'Total Reseller', 'Total Admin', 'Total Client', 'Total Superreseller', 'Minutos']
	# col_model = [{'width': 1, 'align': 'center', 'name': 'client__client'}, {'width': 1, 'align': 'center', 'name': 'destination__destination'},{'width': 1, 'align': 'center', 'name': 'calls'}, {'width': 1, 'align': 'center', 'name': 'non_calls'}, {'width': 1, 'align': 'center', 'name': 'admin_income_currency'}, {'width': 1, 'align': 'center', 'name': 'total_reseller_income'}, {'width': 1, 'align': 'center', 'name': 'total_admin_income'}, {'width': 1, 'align': 'center', 'name': 'total_client_income'}, {'width': 1, 'align': 'center', 'name': 'total_superreseller_income'}, {'width': 1, 'align': 'center', 'name': 'minutes'}]




	return {'view_name':view_name,
			'URL_GRID':URL_GRID,
			'col_name':col_name,
			'col_model':col_model,

			'jsonReader_id':conf_option['jsonReader_id'],
			'multiselect':conf_option['multiselect'],
			'sortname':conf_option['sortname'],
			'footerrow':conf_option['footerrow'],
			'row_num':conf_option['row_num'],
			'subGrid':conf_option['subGrid'],
			'shrinkToFit':conf_option['shrinkToFit'],
			'autowidth':conf_option['autowidth'],#conf_option_default
			'scroll':conf_option['scroll'],#conf_option_default
			'cm_sortable': conf_option['cm_sortable']
			}

##############################################################################################################
############################################--TAG GROUP BY--##################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_group_by.html')
def tag_group_by(view_name,
				grid_name,
				queryset,
				group_by,
				col1=None,
				index1=0,
				col2=None,
				index2=1,
				input_select ='button',
				URL_GRID=None
				):
	"""
	  **Description:**
		This tags create a various buttons or select

	  **Request:**
		>>> {% tag_group_by 'VP' 'VP' queryset group_by col1 0 col2 1 'button' URL_GRID %}
		
	  **Param:**
		#. 'VP' -> view name
		#. 'VP' -> grid name
		#. 'queryset'-> queryset
		#. 'group_by'-> list with group_by
		#. 'col1'-> initial name for column 1
		#. '0'-> index for column 1 (by default 0 if there check 1)
		#. 'col2'-> initial name for column 2
		#. '1'-> index for column 2 (by default 1 if there check 2)
		#. 'button' -> type of imput (button for button or select for select)
		#. 'URL_GRID'-> url declaration in views for refresh grid

	  **Event:** 
		>>> case 'group_by': #when click on shortcuts
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	return {'queryset':queryset,
			'view_name': view_name,
			'grid_name':grid_name,
			'group_by':group_by,
			'col1':col1,
			'index1':index1,
			'index2':index2,
			'col2':col2,
			'URL_GRID':URL_GRID,
			'input_select':input_select
			}

##############################################################################################################
############################################--TAG BUTTON-#####################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_button.html')
def tag_button(view_name,
				button_name,
				button,
				default_value='false',
				input_select='button',
				text_button='Select'
				):
	"""
	  **Description:**
		This tags creates a or various buttons

	  **Request:**
		>>> {% tag_button 'VP' 'data_type' button 'destination' 'button' 'Data type' %}
		
	  **Param:**
		#. 'VP' -> view name
		#. 'data_type' -> button name
		#. button -> list with value of buttons
		#. 'destination'-> default value select in first load
		#. 'button' -> style for button (avaible types is button or select )
		#. 'Data type'-> buttons text

	  **Event:** 
		>>> case 'button': #when click in button
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	return {'view_name': view_name,
			'button':button,
			'default_value':default_value,
			'input_select':input_select,
			'text_button':text_button,
			'button_name':button_name
			}



##############################################################################################################
############################################--TAG EXCEL CSV--#################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_excel_csv.html')
def tag_excel_csv(view_name,
					URL_EXCEL):
	"""
	  **Description:**
		This tags creates two buttons, a for Excel and orther for CSV

	  **Request:**
		>>> {% tag_excel_csv 'VP' URL_EXCEL %}
		
	  **Param:**
		#. 'VP' > view name
		#. 'URL_EXCEL'> the url declaration in views

	  **Event:** 
		>>> case 'excel': #when click in button csv or button excel
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	return {'view_name': view_name,
			'URL_EXCEL':URL_EXCEL
			}



##############################################################################################################
############################################--TAG HIGCHARTS-##################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_highcharts.html')
def tag_highcharts(view_name,data_highcharts, plot_options = {},chart={}):
	"""
	  **Description:**
		This tags creates a graph

	  **Request:**
		>>> {% tag_highcharts 'VP' data_highcharts %}
		
	  **Param:**
		#. 'VP' -> view name
		#. data_higcharts -> dictionary with highcharts data. The estructure is
		data_highcharts = {
		* 'title': title_higcharts,
		* 'position': 'bottom', # postion legend ( bottom or top )
		* 'xAxis': '', #this dict is null because this axis is request of the date
		* 'v_name_y':['ASR','CALLS',''],
		* 'v_dataname':[' %',' Calls',''],
		* 'v_name':dict_higcharts['v_name'],
		* 'v_type':dict_higcharts['v_type'],
		* 'v_yAxis':dict_higcharts['v_yAxis'],
		* 'v_data':data_date,}

	  **Event:** 
		>>> none
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	

	title = data_highcharts['title']

	position = data_highcharts['position']

	xAxis=data_highcharts['xAxis']

	v_name_y = data_highcharts['v_name_y']
	v_dataname= data_highcharts['v_dataname']
	yAxis = get_yAxis(v_name_y,v_dataname)

	v_name = data_highcharts['v_name']
	v_type= data_highcharts['v_type']
	v_yAxis= data_highcharts['v_yAxis']
	v_data= data_highcharts['v_data']

	plot_options_default = {}
	plot_options_default['area'] = {}
	# plot_options_default['area']['stacking'] = 'normal'
	plot_options_default['line'] = {}
	# plot_options_default['line']['stacking'] = 'normal'
 
	plot_options_default['bar'] = {}

	plot_options_default['column'] = {}

	chart_default = {}
	chart_default['renderTo'] = str(view_name)+'_div_highcharts'
	chart_default['marginRight'] = 	130
	chart_default['marginBottom'] = 70
	chart_default['zoomType'] = 'xy'

	chart=updateDict(chart_default,chart)

	plot_options=updateDict(plot_options_default,plot_options)

	try:
		v_color = data_highcharts['v_color']
	except:
		v_color = []

	series = get_series(v_name,v_type,v_yAxis,v_data,v_color)



	return {'view_name': view_name,
			'title':title,
			'position':position,
			'xAxis':xAxis,
			'yAxis':yAxis,
			'series':series,
			'plot_options':plot_options,
			'chart':chart_default,
			'v_color':v_color
			}



##############################################################################################################
############################################--TAG HIGHSTOCK-##################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_highstock.html')
def tag_highstock(view_name,
				URL_HIGHSTOCK,
				data_highcharts
			):
	"""
	  **Description:**
		This tags creates a graph

	  **Request:**
		>>> {% tag_highstock 'asr_acd' URL_HIGHSTOCK data_highstock %}
		
	  **Param:**
		#. 'VP' -> view name
		#. data_highstock -> dictionary with highcharts data. The estructure is
		data_highstock = {
		* 'title': title_higcharts,
		* 'position': 'bottom', # postion legend ( bottom or top )
		* 'xAxis': '', #this dict is null because this axis is request of the date
		* 'v_name_y':['ASR','CALLS',''],
		* 'v_dataname':[' %',' Calls',''],
		* 'v_name':dict_higcharts['v_name'],
		* 'v_type':dict_higcharts['v_type'],
		* 'v_yAxis':dict_higcharts['v_yAxis'],
		* 'v_data':data_date,}

	  **Event:** 
		>>> none
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""

	return {'view_name': view_name,
			'URL_HIGHSTOCK':URL_HIGHSTOCK}


##############################################################################################################
############################################--TAG HIGHSTOCK2-#################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_highstock2.html')
def tag_highstock2(view_name,
					URL_HIGHSTOCK,
					data_highcharts
					):
	"""
	  **Description:**
		This tags creates a graph

	  **Request:**
		>>> {% tag_highstock 'asr_acd' URL_HIGHSTOCK data_highstock %}
		
	  **Param:**
		#. 'VP' -> view name
		#. data_highstock -> dictionary with highcharts data. The estructure is
		data_highstock = {
		* 'title': title_higcharts,
		* 'position': 'bottom', # postion legend ( bottom or top )
		* 'xAxis': '', #this dict is null because this axis is request of the date
		* 'v_name_y':['ASR','CALLS',''],
		* 'v_dataname':[' %',' Calls',''],
		* 'v_name':dict_higcharts['v_name'],
		* 'v_type':dict_higcharts['v_type'],
		* 'v_yAxis':dict_higcharts['v_yAxis'],
		* 'v_data':data_date,}

	  **Event:** 
		>>> none
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	v_name_y = data_highcharts['v_name_y']
	v_dataname= data_highcharts['v_dataname']
	yAxis = get_yAxis(v_name_y,v_dataname)
	return {'view_name': view_name,
			'URL_HIGHSTOCK':URL_HIGHSTOCK,
			'yAxis':yAxis}


##############################################################################################################
############################################--TAG CSV_UPLOAD-#################################################
##############################################################################################################

@register.inclusion_tag('tags/tag_csvupload.html')
def tag_csvupload(view_name,
				UPLOAD_FORM,
				VALIDATE_FORM,
				URL_CSVUPLOAD
				):
	"""
	  **Description:**
		This tags create a button for csv upload

	  **Request:**
		>>> {% tag_excel_csv 'VP' URL_EXCEL %}
		
	  **Param:**
		#. 'VP' -> view name
		#. UPLOAD_FORM -> form
		#. VALIDATE_FORM -> validate form
		#. URL_CSVUPLOAD -> URL upload file

	  **Event:** 
		>>> case 'csvupload': #when click in button
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	return {'view_name': view_name,
			'UPLOAD_FORM':UPLOAD_FORM,
			'VALIDATE_FORM':VALIDATE_FORM,
			'URL_CSVUPLOAD':URL_CSVUPLOAD}




##############################################################################################################
############################################--TAG SLIDER-#####################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_slider.html')
def tag_slider(view_name,
				name_slider,
				text_slider,
				position,
				rang,
				min_val,
				max_val,
				default_min,
				default_max,
				unit,
				vertical ='true',
				):
	"""
	  **Description:**
		This tags create a slider

	  **Request:**
		>>> {% tag_excel_csv 'VP' URL_EXCEL %}
		
	  **Param:**
		#. 'VP' -> view name
		#. 'Number of date' -> slider text
		#. 'horizontal' -> slider position (horizontal or vertical)
		#. 'false' -> false if not have range and true if have range
		#. 0 -> minimun value
		#. 15 -> maximum value
		#. default_min -> default minimun value in first load
		#. default_max -> default maximun value in first load
		#. unit -> measuring unit
		
	  **Event:** 
		>>> case 'slider': #when change value in slider
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	"""
	return {'view_name': view_name,
			'name_slider':name_slider,
			'text_slider':text_slider,
			'position':position,
			'rang':rang,
			'min_val':min_val,
			'max_val':max_val,
			'default_min':default_min,
			'default_max':default_max,
			'unit':unit,
			'vertical':vertical,}



##############################################################################################################
############################################--TAG TABLE-######################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_table.html')
def tag_table(view_name,
				table_dict):
	"""
	  **Description:**
		This tags creates a table

	  **Request:**
		>>> {% tag_table 'VP' table_dict %}
		
	  **Param:**
		#. 'VP'-> view name
		#. table_dict -> dictionary with table date
	  **Event:** 
		>>> none
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	""" 

	return {'view_name': view_name,
			'table_dict':table_dict}


##############################################################################################################
############################################--TAG TABLE-######################################################
##############################################################################################################
@register.inclusion_tag('tags/tag_mail.html')
def tag_mail(view_name,
			mail,
			period,
			URL_MAIL):
	"""
	  **Description:**
		This tags creates a table

	  **Request:**
		>>> {% tag_mail 'VP' mail period URL_MAIL %} 
		
	  **Param:**
		#. 'VP'-> view name
		#. mail -> mail destination
		#. period-> period for send mail
		#. URL_MAIL-> Url for send mail
	  **Event:** 
		>>> Save settings: #when click on button Save Settings
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	""" 
	return {'view_name':view_name,
			'mail':mail,
			'period':period,
			'URL_MAIL':URL_MAIL}



##############################################################################################################
######################################--TAG INTERRUPTOR-######################################################
##############################################################################################################

@register.inclusion_tag('tags/tag_interruptor.html')
def tag_interruptor(view_name,
					interruptor_name,
					name_text,
					callback,
					default_position = 'OFF',
					default_name_OFF = 'OFF',
					default_name_ON='ON'):

	"""
	  **Description:**
		This tags creates a interruptor

	  **Request:**
		>>> {% tag_interruptor 'VP' 'in_asracd' 'ASR/ACD' 'interruptor_asracd_chart' 'ASR' 'ASR' 'ACD' %}
		
	  **Param:**
		#. 'VP' -> view name
		#. 'in_asracd' -> interruptor name
		#. 'ASR/ACD' -> interruptor text
		#. 'interruptor_asracd_chart' -> callback name
		#. 'ASR' -> name for default position
		#. 'ASR' -> name for OFF postion
		#. 'ACD' -> name for ON position
	  **Event:** 
		>>> Save settings: #when click on button Save Settings
  
	  **Import:**
		>>> none
		
	  .. note:: 
		none
	""" 

	return {'view_name':view_name,
			'interruptor_name':interruptor_name,
			'name_text':name_text,
			'callback':callback,
			'default_position':default_position,
			'default_name_OFF':default_name_OFF,
			'default_name_ON':default_name_ON}



def get_field_type(field):
	# fields = self.field
	# print 'fields =',fields
	try:
		if type(field) == unicode:
			return ''
		elif type(field) == long:
			return 'integer'
		elif type(field) == int:
			return 'integer'
		elif type(field) == float: 
			return 'number'
		elif type(field) == Decimal: 
			return 'currency'
		return ''
	except:
		return ''

	return field_types

def getLenMiddle(queryset,col_model):
	dic_len_middle={}
	number_element = queryset.count()
	if number_element > ROWS_TO_EVALUATE:
		number_element = ROWS_TO_EVALUATE

	if number_element == 0:
		dic_len_middle[0]=0
		# raise
	else:
		total_len=0
		for tupla in queryset:
			for q in col_model:
				if q not in dic_len_middle:
					dic_len_middle[q]=0
				value = tupla[q]
				if type(tupla[q]) in [float,Decimal]:
					value=round(value,2)
				dic_len_middle[q] += len(str(value))
		for k,v in dic_len_middle.iteritems():
			dic_len_middle[k]=dic_len_middle[k]/number_element
	return dic_len_middle



def updateDict(dict_default,dict_value):
	new_dict={}
	for j,v_default in dict_default.items():
		replace = True
		for k,v_value in dict_value.items():
			if k == j:
				replace = False
				new_dict[j] = v_value
		if replace == True:    
			new_dict[j] = dict_default[j]
	return new_dict



def getGridConfig(queryset,adjustment_factor,col_order='false',middle_col = 'false',align='center'):

	col_name=[] 
	col_model=[]
	col_len = []
	dic_col_model=[]
	col_types=[]

	col_translations={
		'minutes': _('Minutes'),
		'total_reseller_income':_('Total Reseller'),
		'total_admin_income':_('Total Admin'),   
		'total_client_income':_('Total Client'),
		'total_superreseller_income':_('Total Superreseller'),
		'calls':_('Llamadas'),
		'std_income':_('Standard Income'),
		'destination':_('Destination'),
		'cli_income':_('Client Income'),
		'client':_('Client'),
		'routetable':_('Route Table'),
	}

	group_by_order = ['minutes','calls','total_reseller_income','total_admin_income','total_client_income','total_superreseller_income']

	align=str(align)

	if type(queryset) == django.db.models.query.ValuesQuerySet:
		for i in queryset.field_names:
			# if i != 'id':
			col_name.append(str(unicode(getFieldVerboseName(queryset,i))))
			col_model.append(i)
		for i in queryset.aggregate_names:
			if i in group_by_order:
				col_name.append(str(unicode(col_translations[i])))
			else:
				col_name.append(i)
			
			col_model.append(i)
		for i in queryset.extra_names:
			if i in group_by_order:
				col_name.append(str(unicode(col_translations[i])))
			else:
				col_name.append(i)
			
			col_model.append(i)
	# Instead of a queryset we receive a list of tuples ('Name','field')
	elif type(queryset) == list:
		try:
			if type(queryset[0]) == tuple:
				for i in queryset:
					col_name.append(str(unicode(i[0])))
					col_model.append(i[1])
					col_len.append(i[2])



			elif type(queryset[0]) == dict:
				for i in queryset[0].keys():
					if i in col_translations:
						col_name.append(str(unicode(col_translations[i])))
					else:
						col_name.append(str(unicode(getFieldVerboseName(queryset,i))))                  
					col_model.append(i)
		except:
			logger.error(' getGridConfig: error in len column')


	# Instead of a queryset we receive a dict {'Name':'field'}
	elif type(queryset) == dict:
		for i,j in queryset.items():
			col_name.append(i)
			col_model.append(j)
	
	if middle_col == 'false':

		if type(queryset) == django.db.models.query.ValuesQuerySet:
			try:
				for i in range(0,len(col_model)):
					dic_col_model.append({'name':col_model[i],
										'width':1,
										'align':align,
										})
			except:
				logger.error('getGridConfig: error in asignation len a column of grid')
		elif type(queryset) == list or dict:
			if len(col_len)>0:
				try:
					for i in range(0,len(col_model)):
						dic_col_model.append({'name':col_model[i],
											'width':col_len[i],
											'align':align,
											})
				except:
					logger.error('getGridConfig: error in asignation len a column of grid')
			else:
					for i in range(0,len(col_model)):
						dic_col_model.append({'name':col_model[i],
											'width':1,
											'align':align,
											})

		else:
			for i in col_model:
				dic_col_model.append({'name':i,
									'width':1,
									'align':align,
									'formatter': get_field_type(queryset[0][i])
									})

	else:       
		lenMidle=getLenMiddle(queryset,col_model)
		lenTotal = 0


		for i,k in lenMidle.items():
			if k=='0':
				lenMidle = 'false'
			else:
				lenTotal = lenTotal + k;

		lenTotal = lenTotal / len(lenMidle)

		try:    
			for i in col_model:
				if lenTotal> lenMidle[i]:
					dic_col_model.append({'name':i,
										'width':lenTotal*adjustment_factor,
										'align':align,
										# 'formatter': get_field_type(queryset[0][i])
										}) 
				else:
					dic_col_model.append({'name':i,
										'width':lenMidle[i],
										'align':align,
										# 'formatter': get_field_type(queryset[0][i])
										})
		except:
			for i in col_model:
				dic_col_model.append({'name':i,
								'width':1,
								'align':align,
								# 'formatter': get_field_type(queryset[0][i])
								}) 
			logger.error(' getGridConfig: data passed: lenMidle = {0} lenTotal = {1}'.format(lenMidle,lenTotal))    
			# print 'getGridConfig: data passed: lenMidle = {0} lenTotal = {1}'.format(lenMidle,lenTotal)

	col_model = dic_col_model

	try:
		if col_order != 'false':
			col_model = dic_col_model
			col_model_order=[]
			col_name_order=[]

			for i_order in col_order:
				for col in col_model:
					for i,k in col.items():
						if k == i_order:
							col_model_order.append(col)
							trad = ''
							j = i_order
							if i in col_translations:
								trad = unicode(col_translations[j])
							else:
								trad = str(unicode(getFieldVerboseName(queryset,j)))

							col_name_order.append(trad)

							if trad == '':
								trad = j
			col_name = col_name_order
			col_model = col_model_order
	except:
		logger.error('getGridConfig: order gridname and order gridmodel')
		# print 'getGridConfig: order gridname and order gridmodel'
	return col_name,col_model


# @register.inclusion_tag('tags/grid.html')
# def show_grid(grid):
#   return {'code': grid}



# @register.inclusion_tag('tags/grid.html')
# def show_grid_p(grid, column=None):
#   if column == '': return show_grid(grid)
#   else: return {'code': grid, 'column': column}