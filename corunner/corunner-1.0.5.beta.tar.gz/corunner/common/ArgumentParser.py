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


import NetUtil

def parseHosts(hosts):
	localIP = NetUtil.getLocalIP()
	nodes = []
	splits = hosts.split(",")
	for split in splits:
	        if split.find("..") > 0:
	                segments = split.split("..")
	                if len(segments) != 2:
	                        raise ValueError("Unknown format of hosts: %s"%hosts)
	                if segments[1].find(".") >=0:
	                        raise ValueError("Unknown format of hosts: %s"%hosts)
	                start = 0
	                end = int(segments[1])
	                port = None
	                if segments[0].find(":") > 0:
	                        port = segments[0].split(":")[1]
	                        start = int(segments[0][segments[0].rfind(".")+1:segments[0].rfind(":")])
	                else:
	                        start = int(segments[0][segments[0].rfind(".")+1:])     
	                prefix = segments[0][:(segments[0].rfind(".")+1)]
	                for i in range(start, end+1):
				ip = prefix + str(i)
				if NetUtil.isLocal(ip):
					ip = localIP
	                        if port == None:
	                                nodes.append(ip)
	                        else:
	                                nodes.append(ip + ":" + port)
	        else:
			if NetUtil.isLocal(split):
				nodes.append(localIP)
			else:
	                	nodes.append(split)
	return nodes
