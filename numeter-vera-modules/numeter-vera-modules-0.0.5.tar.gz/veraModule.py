#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
import logging


#
# Vera module
#
class VeraModule:

    def __init__(self, configParser=None):
        self._logger= logging.getLogger(__name__)
        self._logger.info("Plugin Munin start")
        self._configParser=configParser
        self._logfile = 'vera.log'

        self._DATAS = []
        self._INFOS = []
        self._veraData = {}
        self._parsedData = {}

        self._address = '192.168.1.51:3480'

        self._devices = [{'id':5, 'variables':['CurrentTemperature','CurrentSetpoint']},{'id':'8', 'variables':['CurrentLevel']},{'id':'9','variables':['CurrentLevel']},{'id':'7','variables':['CurrentTemperature']}]

        if configParser:
            # Get logfile
            if self._configParser.has_option('VeraModule', 'address')\
                and self._configParser.get('VeraModule', 'address'):
                self._address = self._configParser.get('VeraModule', 'address')

            # Get devices
            if self._configParser.has_option('VeraModule', 'devices')\
                and self._configParser.get('VeraModule', 'devices'):
                self._logger.info(self._configParser.get('VeraModule', 'devices'))
                self._devices = eval(self._configParser.get('VeraModule', 'devices'))

        # Get the data from Vera
        self._parseVERA()

    def _parseVERA(self):
        r = requests.get(self._address.join(['http://', '/data_request?id=user_data2&output_format=json']))
        self._veraData = r.json()

        for device in self._veraData['devices']:
            for device_searched in self._devices:
                if int(device['id']) == int(device_searched['id']):
                    if not str(device['room']) in self._parsedData:
                        self._parsedData[str(device['room'])] = {}
                    if not device['name'] in self._parsedData[str(device['room'])]:
                        variables = {}
                        for variable in device['states']:
                            for variable_searched in device_searched['variables']:
                                if str(variable['variable']) == variable_searched:
                                    variables[str(variable['variable'])] = str(variable['value'])
                        self._parsedData[str(device['room'])][str(device['name'])] = variables

    def _VeraPlugin(self,mode):
        "Vera plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        if mode == 'fetch': # DATAS
            for room, device_list in self._parsedData.items():
                for device_name, device_variables, in device_list.iteritems():
                    self._DATAS.append({
                        'TimeStamp': nowTimestamp,
                        'Plugin': device_name,
                        'Values': device_variables
                    })

            return self._DATAS

        else: # INFOS
            for room, device_list in self._parsedData.items():
                for device_name, device_variables, in device_list.iteritems():
                    dsInfos = {}
                    for variable_name,variable_value in device_variables.items():
                        dsInfos[variable_name] = {
                            "type": "GAUGE",
                            "id": variable_name,
                            "draw": 'line',
                            "label": variable_name}
                    self._INFOS.append({
                        'Plugin': device_name,
                        'Describ': '',
                        'Category': 'Vera',
                        'Base': '1000',
                        'Title': device_name,
                        'Vlabel': '',
                        'Infos': dsInfos,
                    })
            return self._INFOS

    def getData(self):
        "get and return all data collected"
        # Refresh status
        self._VeraPlugin('fetch')
        return self._DATAS

    def getInfo(self):
        "Return plugins info for refresh"
        self._VeraPlugin('config')
        return self._INFOS