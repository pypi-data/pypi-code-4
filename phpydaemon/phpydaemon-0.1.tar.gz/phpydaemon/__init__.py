import multiprocessing, time, logging, bottle, sys, uuid, json, threading, Queue, types, os, subprocess
from json import JSONEncoder
from bottle import route, post, run, template
import daemon, signal, grp, lockfile
from daemon import runner

class Config:

    def __init__(self):
        self.file = '/etc/phpydaemon.json'
        self.data = self.loadFile(self.file)

    def loadFile(self, file):
        if os.path.exists(file):
            fp = open(file, 'r')
            text = fp.read()
            fp.close()
            return json.loads(text)
        else:
            return {}

    def get(self, section, key=None, default=None):
        if key:
            if self.data.has_key(section) and self.data[section].has_key(key):
                return self.data[section][key]
        else:
            if self.data.has_key(section):
                return self.data[section]
        return default

    def getWorker(self, method):
        for worker in self.getWorkers():
            if worker.has_key('method') and worker['method'] == method:
                return worker

    def getWorkerFallback(self):
        for worker in self.getWorkers():
            if worker.has_key('fallback') and worker['fallback']:
                return worker
        return {"fallback": True, "paralell": 2}

    def getWorkers(self):
        workers = self.get('workers')
        if workers:
            return workers
        else:
            return []

    def getDebugLog(self):
        return self.get('log', 'debug', '/var/log/phpydaemon.log')

    def getErrorLog(self):
        return self.get('log', 'error', '/var/log/phpydaemon.err')

    def getPidFile(self):
        return self.get('run', 'pidfile', '/var/run/phpydaemon.pid')

    def getHttpHost(self):
        return self.get('http', 'host', 'localhost')

    def getHttpPort(self):
        return self.get('http', 'port', 9713)

    def getHttpVerbose(self):
        return self.get('http', 'verbose', False)

    def getHttpQuiet(self):
        return not self.getHttpVerbose()

    def getPhpCallback(self):
        return self.get('php', 'callback')

    def validate(self):
        value = self.getPhpCallback()
        if not value:
            raise Exception('Must configure php.callback in %s' % self.file)
        


config = Config()
config.validate()


logger = logging.getLogger('Main')
logger.setLevel(logging.INFO);
#formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(config.getDebugLog())
handler.setFormatter(formatter)
logger.addHandler(handler)

def debug(msg):
    logger.info(msg)

        
# monkey patch json to support Object.to_json()
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)
_default.default = JSONEncoder().default # save unmodified default
JSONEncoder.default = _default # replacement

class JsonSerializable:

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        data = {}
        for key in dir(self):
            if key[0] != '_' and type(getattr(self,key)) != types.MethodType:
                data[key] = getattr(self,key)
        return data
    

class Job(JsonSerializable):

    def __init__(self, method, args, userId):
        self.id     = '%s' % uuid.uuid4()
        self.status = 'queued'
        self.method = method
        self.args   = args
        self.userId = userId


def do_work_php(job):
    debug('do_work_php.start: %s( %s ) : %s' % (job.method, job.args, job.id))
    cmd = [ config.getPhpCallback(), job.to_json() ]
    debug('Running command: %s' % cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = proc.communicate()
    ec = proc.wait()
    if ec != 0:
        debug('ERROR: Command failed with exit code %s: %s\n%s\n%s' % (ec, cmd, out, err))
    else:
        debug('PHP command succeeded. Output: %s' % out)
    debug('do_work_php.end: %s' % job.id)
    
def do_work_dummy(job):
    debug('do_work_dummy.start: %s( %s ) : %s' % (job.method, job.args, job.id))
    time.sleep(2)
    debug('do_work_dummy.end: %s' % job.id)

def worker(jobQueue, returnQueue):
    name = multiprocessing.current_process().name
    debug('worker: Starting worker %s' % name)
    while True:
        #debug('Looking for jobs')
        try:
            job = jobQueue.get(block=True, timeout=2)
        except Queue.Empty:
            continue
        if job == 'QUIT':
            break
        #job = jobQueue.get()
        returnQueue.put(('start', job))
        do_work_php(job)
        jobQueue.task_done()
        returnQueue.put(('done', job))
    debug('worker: Exiting worker %s' % name)


class Register:

    def start(self):
        debug('Register.start start')

        self.config      = config
        self.jobs        = {}
        self.jobCount    = {}
        self.jobQueues   = {}
        self.returnQueue = multiprocessing.Queue()
        self.workers     = []

        # Set up workers for each configured method + one fallback for unconfigured methods
        debug('Setting up workers')
        for workerConfig in self.config.getWorkers():
            id = self.getQueueIdFromWorkerConfig(workerConfig)

            self.jobCount[id]  = 0
            self.jobQueues[id] = multiprocessing.JoinableQueue()
            self.jobs[id]      = []

            count = 1
            if workerConfig.has_key('paralell'):
                count = workerConfig['paralell']

            for i in range(count):
                workerName = 'Worker-%s-%s' % (id,i)
                debug('Creating worker: %s' % workerName)
                w = multiprocessing.Process(
                    name   = workerName,
                    target = worker,
                    args   = (self.jobQueues[id],self.returnQueue),
                )
                w.daemon = True # see quit()
                self.workers.append(w)
                #w.daemon = True
                w.start()

        # Set up thread to process return messages
        debug('Setting up returnQueueThread')
        self.returnQueueThread = ReturnQueueThread()
        self.returnQueueThread.setRegister(self)
        self.returnQueueThread.start()

        debug('Register.start complete')


    # we really don't need to do this, since Popen subprocseses will
    # finish even if the Process that started them dies.
    # so we can just let processes be daemons and die with the parent
    """
    def quit(self):
        for workerConfig in self.config.getWorkers():
            id = self.getQueueIdFromWorkerConfig(workerConfig)
            count = 1
            if workerConfig.has_key('paralell'):
                count = workerConfig['paralell']
            for i in range(count):
                self.jobQueues[id].put('QUIT')
        for worker in self.workers:
            if worker:
                debug('Joining worker %s' % worker.name)
                worker.join()
    """

    def add(self, method, args, userId):
        job = Job(method, args, userId)
        queueId = self.getQueueId(method)
        debug('Add job %s to queue %s : %s( %s )' % (job.id, queueId, job.method, job.args))
        self.jobs[queueId].append(job)
        self.jobQueues[queueId].put(job)
        self.jobCount[queueId] += 1
        return job

    def onJobDone(self, job):
        #debug('onJobDone: %s' % job.id)
        queueId, index = self.findJobIndex(job)
        if queueId:
            debug('onJobDone: Remove job %s with index %s and queueId %s' % (job.id, index, queueId))
            del self.jobs[queueId][index]

    def onJobStart(self, job):
        #debug('onJobStart: %s' % job.id)
        queueId, index = self.findJobIndex(job)
        if queueId:
            debug('onJobStart: Set job %s with index %s and queueId %s as running' % (job.id, index, queueId))
            self.jobs[queueId][index].status = 'running'

    def findJobIndex(self, job):
        index = None
        queueId = self.getQueueId(job.method)
        #debug('findJobIndex: find job with method %s and queueId %s' % (job.method, queueId))
        for i in range(len(self.jobs[queueId])):
            #debug('findJobIndex: check self.jobs[ %s ][ %s ] = %s' % (queueId, i, self.jobs[queueId][i].id))
            if self.jobs[queueId][i].id == job.id:
                index = i
                #debug('findJobIndex: FOUND with index = %s' % index)
                break
        if index != None:
            return (queueId, index)
        else:
            return (None, None)


    def getStats(self):
        stats = {}
        for id in self.jobQueues:
            stats[id] = {
                'queued':  0,
                'running': 0,
                'done':    0
            }
            for job in self.jobs[id]:
                stats[id][job.status] += 1
            stats[id]['done'] = self.jobCount[id] - stats[id]['queued'] - stats[id]['running']
        return stats

    def getJobs(self):
        return self.jobs

    def getQueueId(self, method):
        if self.jobQueues.has_key(method):
            return method
        return self.getFallbackQueueId()

    def getQueueIdFromWorkerConfig(self, workerConfig):
        if workerConfig.has_key('fallback') and workerConfig['fallback']:
            return self.getFallbackQueueId()
        else:
            return workerConfig['method']

    def getFallbackQueueId(self):
        return 'FALLBACK'


class ReturnQueueThread(threading.Thread):

    def __init__(self, *args, **kw):
        threading.Thread.__init__(self, *args, **kw)
        self.setDaemon(True)

    def setRegister(self, register):
        self.register = register
        self.queue = self.register.returnQueue

    def run(self):
        while True:
            if self.queue:
                try:
                    action, job = self.queue.get(block=True, timeout=2)
                    if action == 'done':
                        self.register.onJobDone(job)
                    elif action == 'start':
                        self.register.onJobStart(job)
                except Queue.Empty:
                    pass
        

register = Register()


@post('/api/run')
def w_api_run():
    if not bottle.request.json.has_key('method') or not bottle.request.json['method']:
        return 'ERROR: must have "method" in request json data'
    method = bottle.request.json['method']
    args = []
    if bottle.request.json.has_key('args') and bottle.request.json['args']:
        args = bottle.request.json['args']
    userId = None
    if bottle.request.json.has_key('userId') and bottle.request.json['userId']:
        userId = bottle.request.json['userId']
    job = register.add(method, args, userId)
    return job.to_dict()

@route('/api/stats')
def w_api_stats():
    return register.getStats()

@route('/api/jobs')
def w_api_jobs():
    data = {}
    jobs = register.getJobs()
    for queueId in jobs:
        for job in jobs[queueId]:
            if not data.has_key(queueId):
                data[queueId] = []
            data[queueId].append(job.to_dict())
    return data

@route('/status')
def w_status():
    config = register.config.getWorkers()
    try:
        paralell = {'FALLBACK': register.config.getWorkerFallback()['paralell']}
    except:
        paralell = {'FALLBACK': 1}
    for item in config:
        if item.has_key('method'):
            if item.has_key('paralell'):
                paralell[item['method']] = item['paralell']
            else:
                paralell[item['method']] = 1
    data = {
        'stats':    register.getStats(),
        'jobs':     register.getJobs(),
        'paralell': paralell
    }
    return template('templates/status', data=data)

@route('/')
def w_index():
    return template('templates/index')

class App():
    
    def __init__(self):
        self.stdin_path       = '/dev/null'
        self.stdout_path      = '/dev/null'
        self.stderr_path      = config.getErrorLog()
        self.pidfile_path     = config.getPidFile()
        self.pidfile_timeout  = 5
            
    def run(self):
        register.start()
        run(host=config.getHttpHost(), port=config.getHttpPort(), quiet=config.getHttpQuiet())

""" not needed - see comment on Register.quit()
def on_sigterm(sig, frame):
    if os.getppid() != 1:
        debug('Ignoring kill signal since I am child')
        return
    debug('Signaling children top stop...')
    register.quit()
    debug('Exiting...')
    sys.exit()
"""

def main():
    wd = os.path.dirname(os.path.realpath(__file__));

    app = App()

    r = runner.DaemonRunner(app)
    r.daemon_context.files_preserve    = [handler.stream]
    r.daemon_context.working_directory = wd
    ''' does not work well with children - they catch it too '''
    '''
    r.daemon_context.signal_map = {
        signal.SIGTERM: on_sigterm
    }
    '''
    #r.daemon_context.gid = grp.getgrnam('www-data').gr_gid
    #r.daemon_context.uid = ...

    r.do_action()

if __name__ == '__main__':
    main()
