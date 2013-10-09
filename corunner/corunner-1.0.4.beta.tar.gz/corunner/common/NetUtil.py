# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Author: zwsun<sun33170161@gmail.com>


import os
import socket

if os.name != "nt":
	import fcntl
	import struct

def getInterfaceIP(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
		)[20:24])

def getLocalIP():
	ip = socket.gethostbyname(socket.gethostname())
	if ip.startswith("127.") and os.name != "nt":
		interfaces = [
			"eth0",
			"eth1",
			"eth2",
			"wlan0",
			"wlan1",
			"wifi0",
			"ath0",
			"ath1",
			"ppp0",
			]
		for ifname in interfaces:
			try:
				ip = getInterfaceIP(ifname)
				break
			except IOError:
				pass
	localIP = ip
	return localIP

LOCAL_IP = getLocalIP()

def isLocal(addr):
	return addr == "localhost" or addr == "127.0.0.1" or addr == LOCAL_IP
	
