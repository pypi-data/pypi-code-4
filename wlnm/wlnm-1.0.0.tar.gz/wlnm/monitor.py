'''

monitor.py
==========

Desc: Function for list all process running on the machine , showing status of each process


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import psutil
import datetime

import util

def listprocess():
	#print util.daemonStatus
	

	_table = [["Name", "CPU%", "MEM%" ,"THREADS","UPTIME+","PID"]]
	
	#serversDB,servers = util.loadDB(server=True)[2]
	

	for p in psutil.process_iter():
		for subcmd in p.cmdline :
			if '-Dweblogic.Name=' in subcmd :
				_table.append([subcmd.split("=")[-1], "%.2f" % p.get_cpu_percent(), "%.2f" % p.get_memory_percent(), p.get_num_threads(),datetime.datetime.now().replace(microsecond=0)-datetime.datetime.fromtimestamp(p.create_time).replace(microsecond=0),p.pid])
				
				
	util.pprint_table(_table)


def isRunning(server):
	_status = 'DOWN'

	for p in psutil.process_iter():
		if '-Dweblogic.Name=%s' % server in p.cmdline :
			_status = 'UP'

	return _status

