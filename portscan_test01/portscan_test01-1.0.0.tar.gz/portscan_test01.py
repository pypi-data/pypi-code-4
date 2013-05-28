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
		banner=retBanner(ip,port)
		print(banner)
if __name__ == '__main__' :
	main()
