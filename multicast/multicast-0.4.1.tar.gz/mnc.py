#!/usr/bin/python -u

import logging
logging.basicConfig(level=logging.DEBUG)

import multicast

def argmain():
	import argparse

	p = argparse.ArgumentParser()

	p.add_argument('-p', '--port', default=4242, help='Port to listen on/send to')
	p.add_argument('-a', '--addr', default='224.0.42.42', help='Multicast group/address to join')
	p.add_argument('-s', '--server', action='store_true', help='Listen for and dump multicast packets on the specified address and port')

	args = p.parse_args()

	logger = logging.getLogger('mcast')

	
	if args.server:
		def packet_handler(packet, addr):
			print addr, packet
		multicast.listen(packet_handler, args.addr, args.port)
	else:
		def packet_generator():
			import sys

			for line in sys.stdin:
				yield line.strip()
		print 'Ready to send... send EOF twice to quit.'
		multicast.sendto(packet_generator(), args.addr, args.port)

argmain()