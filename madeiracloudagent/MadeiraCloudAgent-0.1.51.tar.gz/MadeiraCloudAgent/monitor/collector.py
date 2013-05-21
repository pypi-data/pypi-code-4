import os,time
from decimal import *

class Monitor_Collector():
	
	def __init__(self):
		self._CLOCK_TICKS = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
		self.data_package 	= 	{'CPU_us' 	: 0,\
								 'CPU_ni' 	: 0,\
								 'CPU_sy' 	: 0,\
								 'CPU_id' 	: 0,\
								 'CPU_wa' 	: 0,\
								 'CPU_hi' 	: 0,\
								 'CPU_si' 	: 0,\
								 'CPU_st' 	: 0,\
								 'CPU_gu' 	: 0,\
								 'mem_t' 	: 0,\
								 'mem_f' 	: 0,\
								 'mem_p' 	: 0,\
								 'vmem_t' 	: 0,\
								 'vmem_f' 	: 0,\
								 'vmem_p' 	: 0,\
								 'mem_bu_p' : 0,\
								 'mem_ca_p' : 0,\
								 'd_t' 		: "",\
								 'd_f' 		: "",\
								 'd_p' 		: "",\
								 'd_d' 		: "",\
								 'disk' 	: "",\
								 'io_r' 	: 0,\
								 'io_w' 	: 0,\
								 'io_rb' 	: 0,\
								 'io_wb' 	: 0,\
								 'io_rt' 	: 0,\
								 'io_wt' 	: 0,\
								 'b_s_ps' 	: 0,\
								 'b_r_ps' 	: 0,\
								 'p_s_ps' 	: 0,\
								 'p_r_ps' 	: 0,\
								 'load' 	: 0,\
								 'time' 	: 0}
		self.package_names = ['CPU_us', 'CPU_ni', 'CPU_sy', 'CPU_id', 'CPU_wa', 'CPU_hi', 'CPU_si', 'CPU_st', 'CPU_gu','CPU','mem_t', 'mem_f', 'mem_p', 'vmem_t', 'vmem_f', 'vmem_p', 'mem_bu_p', 'mem_ca_p','d_t','d_f','d_p','d_d','disk', 'io_r','io_w','io_rb','io_wb', 'io_rt', 'io_wt','b_s_ps','b_r_ps','p_s_ps','p_r_ps','load','time','format']
		self.begging = True
		self.internal_data = None
		self.timestamp = 0
		
	def get_system_cpu_times(self):
		"""	
		user, nice, system, idle, iowait, irq, softirq, steal, guest.
		"""
		f = open('/proc/stat', 'r')
		try:
			values = f.readline().split()
		finally:
			f.close()
		if len(values) < 10:
			for i in range(10 - len(values)):
				values.append(0)
		values = values[1:10]
		#names  = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest']	
		values = [float(x) / self._CLOCK_TICKS for x in values]
		#return_values = dict(zip(names,values))
		#values = dict(x for x in names ,float(x) / _CLOCK_TICKS for x in values)
		return values
	
	def cpu_usage(self,cpu_start, cpu_end):
		"""
		Return network usage for all interface and count per second
		"""
		values = [ ((y - x)/5) for x, y in zip(cpu_start, cpu_end)]
		#names = ['CPU_us', 'CPU_ni', 'CPU_sy', 'CPU_id', 'CPU_wa', 'CPU_hi', 'CPU_si', 'CPU_st', 'CPU_gu']
		#to_display_cpu = cpu - self.cpu
		total = 0
		for x in values:
			total += x
		tmp = []
		total_cpu_usage = 0
		for x in values:	
			tmp.append(float(x) / total)
		for x in tmp:	
			total_cpu_usage += x
		total_cpu_usage -= tmp[3] 
		tmp.append(total_cpu_usage)
		values = tmp
		return values
				
		"""	
		last_times = self.get_system_cpu_times()
		last_total = 0
		for x in last_times:
			last_total += x
		time.sleep(0.1)
		times = self.get_system_cpu_times()
		total = 0
		for x in times:
			total += x
		time_diff = total - last_total
		names  = ['CPU_us', 'CPU_ni', 'CPU_sy', 'CPU_id', 'CPU_wa', 'CPU_hi', 'CPU_si', 'CPU_st', 'CPU_gu']	
		values = ['%.4f' % ((x - y) /time_diff) for x,y in zip(times, last_times)]
		return_values = dict(zip(names,values))
		return_values['CPU'] = '%.4f' % (1 - float(return_values['CPU_id'])) 
		return return_values
		"""
		
	def mem_usage(self):
		"""	
		MemTotal:      2074992 kB
		MemFree:        584120 kB
		Buffers:        262300 kB
		Cached:         891332 kB
		SwapTotal:     4128696 kB
		SwapFree:      4128696 kB
		"""
		f = open('/proc/meminfo', 'r')
		try:
			total = free = buffered = cached = swapcached = swapfree = swaptotal = None
			for line in f:
				if line.startswith('MemTotal:'):
					total = int(line.split()[1]) * 1024
				elif line.startswith('MemFree:'):
					free = int(line.split()[1]) * 1024
				elif line.startswith('Buffers:'):
					buffered = int(line.split()[1]) * 1024
				elif line.startswith('Cached:'):
					cached = int(line.split()[1]) * 1024            
				elif line.startswith('SwapTotal:'):
					swaptotal = int(line.split()[1]) * 1024
				elif line.startswith('SwapFree:'):
					swapfree = int(line.split()[1]) * 1024
				#if total is not None and free is not None:
				#    break
			# total is not None and free is not None
			#names = ['mem_t', 'mem_f', 'mem_p', 'vmem_t', 'vmem_f', 'vmem_p', 'mem_bu_p', 'mem_ca_p']
			swap_p = 0
			try:
				swap_p = float(swaptotal - swapfree)/ swaptotal
			except ZeroDivisionError:
				swap_p = 0
			values = [total, free, float(total - free) / total, swaptotal, swapfree, swap_p, float(buffered)/ total, float(cached)/ total ]
			#percent = usage_percent(used, total, _round=1)
			return values
		finally:
			f.close()
	
	def disk_partitions(self,all=False):  
		"""
		Return all mountd partitions as a dict.    
		"""  
		phydevs = []  
		f = open("/proc/filesystems", "r")  
		for line in f:  
			if not line.startswith("nodev"):  
				phydevs.append(line.strip())  
	  
		retlist = {} 
		f = open('/etc/mtab', "r")  
		for line in f:  
			if not all and line.startswith('none'):  
				continue  
			fields 				= line.split()  
			device 				= fields[0]  
			mountpoint 			= fields[1]  
			fstype 				= fields[2]  
			if not all and fstype not in phydevs:  
				continue  
			if device == 'none':  
				device 			= ''
			#ntuple = disk_ntuple(device, mountpoint, fstype)  
			retlist[device]		= mountpoint
		return retlist  
	
	def disk_usage(self):  
		"""Return disk usage associated with path."""  
		disk 					= self.disk_partitions()
		#names 					= ['d_t','d_f','d_p','d_d','disk']
		free 					= ""
		total 					= ""
		percent 				= ""
		devices 				= ""
		disks					= ""
		for device in disk.keys():
			devices += device + ";"
			disks += disk[device] + ";"
			st = os.statvfs(disk[device])  
			free += str(st.f_bavail * st.f_frsize)   + ";" 
			total += str(st.f_blocks * st.f_frsize)   + ";" 
			used = (st.f_blocks - st.f_bfree) * st.f_frsize  
			try:  
				percent += str(float(used) / (st.f_blocks * st.f_frsize))  + ";" 
			except ZeroDivisionError:  
				percent += '0' + ";" 
		disks 					= disks.strip(';')
		free 					= free.strip(';')
		total 					= total.strip(';')
		percent 				= percent.strip(';')
		devices 				= devices.strip(';')
		values 					= [total,free,percent,devices,disks]
		# NB: the percentage is -5% than what shown by df due to  
		# reserved blocks that we are currently not considering:  
		# http://goo.gl/sWGbH  
		return values
	
	def disk_io_counters(self):
		"""
		Return disk I/O statistics for every disk installed on the
		system as a dict of raw tuples.
		"""
		# man iostat states that sectors are equivalent with blocks and
		# have a size of 512 bytes since 2.4 kernels. This value is
		# needed to calculate the amount of disk I/O in bytes.
		SECTOR_SIZE = 512	
		# determine partitions we want to look for
		partitions = []
		f = open("/proc/partitions", "r")
		try:
			lines = f.readlines()[2:]
		finally:
			f.close()
		for line in lines:
			_, _, _, name = line.split()
			if name[-1].isdigit():
				partitions.append(name)    
		retdict = {}
		io_r 	= 0
		io_w 	= 0
		io_rb 	= 0
		io_wb 	= 0
		io_rt 	= 0
		io_wt 	= 0
		
		f = open("/proc/diskstats", "r")
		try:
			lines = f.readlines()
		finally:
			f.close()
		for line in lines:
			_, _, name, reads, _, rbytes, rtime, writes, _, wbytes, wtime = \
				line.split()[:11]
			if name in partitions:            
				io_rb += int(reads)
				io_wb += int(writes)
				io_r += int(rbytes) * SECTOR_SIZE
				io_w += int(wbytes) * SECTOR_SIZE
				io_rt += int(rtime)
				io_wt += int(wtime)
				#retdict[name] = [reads, writes, rbytes, wbytes, rtime, wtime]   
		return [io_rb,io_wb,io_r,io_w, io_rt, io_wt]
		
	def io_usage(self,io_start,io_end, time):
		"""
		Return io usage for all disk and count per second
		"""
		values = [ ((y - x)/time) for x, y in zip(io_start, io_end)]
		#names = ['io_r','io_w','io_rb','io_wb', 'io_rt', 'io_wt']
		return values
		
	def network_io_counters(self):
		"""
		Return network I/O statistics for all network interface    
		"""
		f = open("/proc/net/dev", "r")
		try:
			lines = f.readlines()
		finally:
			f.close()
	
		retdict = {}
		b_s 	= 0
		b_r 	= 0
		p_s 	= 0
		p_r 	= 0
		for line in lines[2:]:
			name = line.split(":")[0]
			fields = line.split(":")[1].split()
			b_r += int(fields[0])
			p_r += int(fields[1])
			b_s += int(fields[8])
			p_s += int(fields[9])
			#retdict[name] = (bytes_sent, bytes_recv, packets_sent, packets_recv)
		return [b_s, b_r, p_s, p_r]
		
	def network_usage(self,net_start,net_end, time):
		"""
		Return network usage for all interface and count per second
		"""
		values = [ ((y - x)/time) for x, y in zip(net_start, net_end)]
		#names = ['b_s_ps','b_r_ps','p_s_ps','p_r_ps']
		return values
		
	def load_usage(self):
		tmp = os.getloadavg()[0]
		return [tmp]
	
	def format_float(self, float_ary):
		tmp = []
		for x in float_ary:
			tmp.append("%.4f" % x)
		return tmp
		
	def update(self):
		if self.begging:
			self.timestamp 	= time.time()
			self.cpu 		= self.get_system_cpu_times()
			self.mem 		= self.mem_usage()
			self.disk 		= self.disk_usage()
			self.io 		= self.disk_io_counters()
			self.net_io 	= self.network_io_counters()
			self.load		= self.load_usage()
			self.internal_data = [0,0,0,0,0,0,0,0,0,0]+self.mem+self.disk+[0,0,0,0,0,0]+[0,0,0,0]+self.load+[self.timestamp]
			self.begging 	= False
			
		else:		
			times 			= time.time()
			cpu 			= self.get_system_cpu_times()
			io 				= self.disk_io_counters()
			net_io 			= self.network_io_counters()
			mem 			= self.mem_usage()
			disk 			= self.disk_usage()
			load 			= self.load_usage()
			
			to_display_cpu 	= self.cpu_usage(self.cpu,cpu)
			to_display_mem 	= mem
			to_display_disk = disk
			to_display_io	= self.io_usage(self.io,io, times - self.timestamp)
			to_display_net_io	= self.network_usage(self.net_io,net_io, times - self.timestamp)
			to_display_load 	= load
			self.internal_data 	= self.format_float(to_display_cpu)\
								+ self.format_float(to_display_mem)\
								+ to_display_disk\
								+ self.format_float(to_display_io)\
								+ self.format_float(to_display_net_io)\
								+ self.format_float(to_display_load) \
								+ [self.timestamp]
			
			self.cpu 		= cpu
			self.mem 		= mem
			self.disk 		= disk
			self.io 		= io
			self.net_io 	= net_io
			self.load		= load			
			self.timestamp 	= times
			
	def display(self):
		to_send = self.internal_data
		to_send.append(0)		
		return dict(zip(self.package_names,to_send))
			
	def test(self):	
		print
		
		print "---------Test Memory usage--------"
		print self.mem_usage()
		
		print
		print "---------Test CPU usage--------"
		print self.cpu_usage()
		
		print
		print "---------Test Disk usage--------"
		print self.disk_usage()
		
		print
	
		
		
if __name__ == '__main__':	
	#print get_system_cpu_times()
	#test()
	abc = Monitor_Collector()
	
	for i in range(10):
		abc.update()
		print abc.display()
		time.sleep(5)
	
