#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import xmltodict


class Yo(object):
    def __init__(self, username, password, method, url, **kwargs):
	self.method = method
	self.extra_data = kwargs
	self.username = username
	self.password = password
	self.url = url

    def get_username(self):
	return self.username

    def get_password(self):
	return self.password

    def parse_response(self, response):
	data = xmltodict.parse(response.text)
	return data


    def make_request(self):
	response = requests.post(self.get_api_url(), data=self.get_xml_data(), headers=self.get_headers(), verify=False)
	return self.parse_response(response)

    def get_api_url(self):
	return self.url()

    def get_headers(self):
	return {'Content-Type': 'text/xml', 'Content-transfer-encoding:': 'text'}

    def get_xml_data(self):
	data = """<?xml version="1.0" encoding="UTF-8"?>
<AutoCreate>
<Request>
 <APIUsername>{username}</APIUsername>
 <APIPassword>{password}</APIPassword>
 <Method>{method}</Method>
 {extra_xml}
 </Request>
</AutoCreate>
	""".format(username=self.get_username(), password=self.get_password(), method=self.get_method(),
		   extra_xml=self.extra_xml())
	return data

    def get_method(self):
	return self.method

    def extra_xml(self):
	output = ""
	for key, value in self.extra_data.iteritems():
	    output += "<{key}>{value}</{key}>".format(key=key, value=value)
	return output