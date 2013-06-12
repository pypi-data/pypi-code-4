'''

webserver.py
==========

Desc: web server of wlnm


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 


'''

import os
from os import environ as env
import sys
import bottle
from bottle import route, run, static_file, redirect, request, error
from beaker.middleware import SessionMiddleware
import server ,util,database
from os.path import expanduser

from daemon import Daemon

bottle.debug(True)

WEBPATH = os.path.dirname(os.path.abspath(__file__))
webroot = '%s/app' % WEBPATH


# session set up
app = bottle.default_app()
session_opts = {
	#'session.type': 'file',
	'session.cookie_expires': 30000,
	#'session.data_dir': './session',
	'session.auto': True,
	'session.type': 'memory',
	#'session.key' : 'wlnm',
	#session.secret = 0cb243f53ad865a0f70099c0414ffe9cfcfe03ac
}
app = SessionMiddleware(app, session_opts)


# static files (js,css,templates) set up

@route('/lib/:path#.+#')
def server_static(path):
    return static_file(path, root='%s/lib/' % webroot)
'''
@route('/scenarios.js')
def scenario():
    return static_file('scenarios.js',root='./test/e2e/')
'''
@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root=webroot)

@route('/js/:path#.+#')
def server_static(path):
    return static_file(path, root='%s/js/' % webroot)

@route('/css/:path#.+#')
def server_static(path):
    return static_file(path, root='%s/css/' % webroot)

@route('/img/:path#.+#')
def server_static(path):
    return static_file(path, root='%s/img/' % webroot)

@route('/templates/:path#.+#')
def server_static(path):
    return static_file(path, root='%s/templates/' % webroot)

# route set up
@route('/settings',method='POST')
def save_settings():
    s = request.environ.get('beaker.session')
    s['wlnm'] = request.POST.get('machine').strip()
    s.save()
    redirect ('/')


@route('/command/:id',method='GET')
def get_commands(id):
     args = id.split(" ")[1:]
     cmd = id.split(" ")[0]
     result = run_command(cmd,args)
     return result


@route('/')
@route('/index.html')
def index():
    raise static_file('index.html', root=webroot)

'''
@route('/tests')
def tests():
    raise static_file('runner.html', root='./test/e2e/')
'''


@error(404)
def mistake404(code):
    return static_file('404.html', root=webroot)


def runServer(port):
    bottle.run(app=app,host='0.0.0.0', port=port)

def saveMachine(machine):
	s = request.environ.get('beaker.session')

	s['machine'] = machine

	s.save()

	return 'Machine %s is set!' % machine

def ifSession(key):
	try :
		s = request.environ.get('beaker.session')
		print s
		if key in s.keys():
			return True
		else :
			return False
	except :
		return False


def run_command(cmd,args=[]):
	

	machine =''
	
	if ifSession('machine'):
		s = request.environ.get('beaker.session')
		machine = s['machine']
		print machine


	cmddict={'init':server.initMachine,
		'ls':server.show,
		'lswls':server.showWLS,
		'lsd':server.showDomains,
		'lsm':server.showMachines,
		'nmstart':server.nmstart,
		'help':util.help,
		'startadmin':server.startAdmin,
		'start':server.startServer,
		'stop':server.stopServer,
		'lsp':server.listprocess,
		'kill':server.kill,
		'use':server.useMachine,
		# 'disconnect':server.disconnect,
		}
	
	if cmd not in cmddict.keys():
		return 'invalid command , use help to check commands.'

	if cmd not in ['help','lsm','use','init'] and not machine :
		return 'you must connect one machine to use %s' % cmd
		
	
	if cmd == 'help' :
		mystdout,old_stdout = util.redirectStdout()
		cmddict[cmd]()
		util.finishRedirectStdout(old_stdout)
		return mystdout.getvalue()
	elif cmd == 'use' :
		try:
			result = cmddict[cmd](args) 
			port = int(result)
			saveMachine(args[0])
			return '%s is ready to use . ' % args[0]
			
		except:
			return result
	elif cmd == 'init' :
		return cmddict[cmd](args[0],args[1])
	elif cmd == 'lsm' :
		return util.decode_output(cmddict[cmd]())
	elif cmd in ['lswls','lsp','lsd']:
		return util.decode_output(cmddict[cmd](machine))
	else :
		#args.insert(0,cmd)
		args.insert(0,machine)
		print args
		return util.decode_output(cmddict[cmd](args))

	

# start application
#database.checkdb()
#bottle.run(app=app,host='0.0.0.0', port=argv[1])

wlnws_pid_file = "%s/.wlnm/wlnws.pid" % expanduser("~")

database.creatProfileDir()

class webserverDaemon(Daemon):

	def __init__(self,pidfile, port,stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, home_dir='.', umask=022, verbose=1):
		wlnws_out_file = "%s/.wlnm/wlnws.out" % expanduser("~")
		self.stdin = stdin
		self.stdout = wlnws_out_file
		self.stderr = wlnws_out_file
		self.pidfile = pidfile
		self.home_dir = home_dir
		self.verbose = verbose
		self.umask = umask
		self.daemon_alive = True
		self.port = port
	

	def start(self):

		# Check port see if it is open
		if util.checkport(self.port) :
			message = "port %s is occupied by other process\n"
                        sys.stderr.write(message % self.port)
                        sys.exit(1)
		super(webserverDaemon, self).start()

	def run(self):
		try:
			database.checkdb()
			bottle.run(app=app,host='0.0.0.0', port =self.port)
		except Eception,e:
			print e
			sys.exit(1)

def runDaemon(iport):
	print "Start wlnm web server daemon ."
	daemon = webserverDaemon(pidfile=wlnws_pid_file,port=iport)
	daemon.start()
	


def stopDaemon():
	
	if os.path.isfile(wlnws_pid_file):
	    with open(wlnws_pid_file) as f:
		pids = f.readlines()
	    try:
		os.kill(int(pids[0]),9)	#force kill
		print "wlnm web server process %s is stopped ." % int(pids[0])
	    except :
		print "wlnm web server process %s was killed before ." % int(pids[0])
	    finally :
		os.remove(wlnws_pid_file)
	else :
	    print "wlnm server is not running , no process can be stopped."
	
	print