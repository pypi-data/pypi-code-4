import random

from shelljob import job

jm = job.FileMonitor(feedback_timeout = 0.5)

cmds = [ [ 'ls', '-alR', '/usr/local/' ] for i in range(0,20) ]
cmds += [ [ 'ls', '-alR', '/usr/local/{}'.format(i) ] for i in range(0,20) ]
random.shuffle(cmds)

jm.run( cmds )
