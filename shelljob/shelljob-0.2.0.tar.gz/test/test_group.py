import sys

from shelljob import proc

sp = proc.Group()

for i in range(0,5):
	sp.run( ['ls', '-al', '/usr/local'] )
while sp.is_pending():
	lines = sp.readlines()
	for proc, line in lines:
		sys.stdout.write( "{}:{}".format( proc.pid, line ) )
