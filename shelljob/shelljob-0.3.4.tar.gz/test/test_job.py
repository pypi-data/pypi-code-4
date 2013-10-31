import random

from shelljob import job

jm = job.FileMonitor(feedback_timeout = 0.5)


cmds = [ [ 'ls', '-alR', '/usr/local/' ] for i in range(0,20) ]
# plain strings can be used (note these ls commands are expected to fail)
cmds += [ 'ls -alR /usr/local/{}'.format(i) for i in range(0,10) ]
# explicits Jobs can be created
def gen_job(i):
	obj = job.Job( 'echo {}'.format(i) )
	obj.name = 'Echo #{}'.format(i)
	return obj
cmds += [ gen_job(i) for i in range(0,10) ]

random.shuffle(cmds)

jm.run( cmds )
