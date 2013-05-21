#!/usr/bin/env python

import sys, time, base64
import httplib, urllib, urllib2
import re,os

from collector import Monitor_Collector


class Madeira():
	
	def decodeUsage(self,string):	
		substring = str(string).split('(')[1]
		substring_type = re.findall("[a-z]+\_[a-z]+|[a-z]+",substring)
		substring_value =  re.findall("\d+\.\d+|\d+",substring)
		return substring_type, substring_value
	
	def getParams(self,param,name,data):	
		data_type,data_value = self.decodeUsage(data)
		for i in range(0,len(data_type)):
			param[name +"_" + data_type[i]] = data_value[i]
		return param
	
	def updateKey(self):
		try:
			response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id')
			instance_id = response.read()
			profilereader = open("/usr/local/madeiracloud/profile.madeira")
			userid = ''
			for line in profilereader:
				userinfo = line.split('=')
				if userinfo[0].strip()=='userid':
					userid = userinfo[1].strip()				
			data = open('/usr/local/madeiracloud/profile.madeira').read()
			data = re.sub('^access_key.*','access_key='+userid+"-"+instance_id, data) 
			open('/usr/local/madeiracloud/profile.madeira', 'wb').write(data)
		except Exception,msg:
			print msg
		
		
	def run(self):
		self.updateKey()
		t = time.time()
		collector = Monitor_Collector()

		while True:
			try:
				start_time = time.time()
				if start_time - t > 3600:
					self.updateKey()
						
				profilereader = open("/usr/local/madeiracloud/profile.madeira")
				for line in profilereader:
					userinfo = line.split('=')
					if userinfo[0].strip()=='userid':
						userid = userinfo[1].strip() 
					if userinfo[0].strip()=='access_key':
						access_key = userinfo[1].strip()
				

				collector.update()
				
				param = collector.display()
				param['key']= access_key
				param['userid']=userid


				username = param['userid']
				
				# new api
				#password = 'x'
				#auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
				#params = urllib.urlencode(param) 
				#request = urllib2.Request("https://api.madeiracloud.com/monitor/new_data")				
				#request.add_header("Authorization", "Basic %s" % auth)   
				#request.add_header("Content-type", "application/x-www-form-urlencoded") 
				#request.add_header("Accept", "text/plain")     
				#response = urllib2.urlopen(request, params)
					
				# old api
				url = '?method=record_instance_data';
				for key in param.keys():
					url = url+"&"+key+"="+str(param[key])
				conn = httplib.HTTPSConnection("api.madeiracloud.com")				
				conn.request("GET", "/monitor/"+url)
				response = conn.getresponse()
				
				#headers = {"Authorization": "Basic "+ auth,"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
				#conn = httplib.HTTPSConnection("api.madeiracloud.com")			
				#conn.request("POST", "/monitor2/new_data",param , headers)
				#response = conn.getresponse()
				#conn.close()
				
				command = response.read()
				command = command.strip()
				

				toDo = {}				

				ary = command.split(';')
				for opt in ary:
					if opt.strip() == '':
						continue
					tmp = opt.split(':')
					if(len(tmp)==1):
						continue
					toDo[tmp[0]] = tmp[1]
				#print toDo
				if "Stop" in command:
					os.system("service madeiracloud stop")


				end_time = time.time()
				diff = end_time - start_time
				if diff >=4.98:
					continue
				sleep_time = 4.98 - diff
				time.sleep(sleep_time)
			except Exception, msg:		
				try:
					# new api
					#username = param['userid']
					#password = 'x'
					#auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
					#param = urllib.urlencode({'msg':str(msg), 'key': access_key}) 
					#request = urllib2.Request("https://api.madeiracloud.com/monitor/new_error")				
					#request.add_header("Authorization", "Basic %s" % auth)   
					#response = urllib2.urlopen(request, param)
					#response.read()
					
					# old api
					conn = httplib.HTTPSConnection("api.madeiracloud.com")
					conn.request("GET", "/monitor/?method=errorReport&msg="+str(msg)+"&key="+access_key)
					response = conn.getresponse()
					response.read()
					conn.close()
					time.sleep(120)
					continue
				except Exception, msg1:	
					continue

if __name__ == "__main__":
	daemon = Madeira()
	daemon.run()

