import sys
import socket
socket.setdefaulttimeout(2)
def retBanner(ip,port):
	try:
		s=socket.socket()
		s.connect((ip,port))
		banner=s.recv(1024)
		return(banner)
	except:
		return(None)
def main():
	s=socket.socket()
	if not len(sys.argv)==3:
		print("Usage : "+sys.argv[0]+" IPAddress PORT")
	else:		
		ip=sys.argv[1]
		port=int(sys.argv[2])
		result=list(ip)	
		if '/' in result :
			ip1=ip.split("/")
		
			if int(ip1[1])==24:
				splitter=ip.split('.',3)
				for i in range(1,255):
					splitter[3]=str(i)
					t=".".join(splitter)
					banner=retBanner(t,port)
					print(banner)	
		else:
			banner=retBanner(ip,port)
			print(banner)
if __name__ == '__main__' :
	main()
