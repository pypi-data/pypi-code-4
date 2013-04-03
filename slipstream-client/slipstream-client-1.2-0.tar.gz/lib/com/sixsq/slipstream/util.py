import logging
import os
import sys
import time
import uuid as uuidModule
from ConfigParser import SafeConfigParser
import urllib2
import subprocess
import tempfile

import com.sixsq.slipstream.exceptions.Exceptions as Exceptions

timeformat = '%Y-%m-%d %H:%M:%S'

VERBOSE_LEVEL_QUIET = 0
VERBOSE_LEVEL_NORMAL = 1
VERBOSE_LEVEL_DETAILED = 2

PRINT_TO_STDERR_ONLY = False

TMPDIR = os.path.join(os.sep, 'tmp', 'slipstream')
REPORTSDIR = os.environ.get('SLIPSTREAM_REPORT_DIR', os.path.join(os.sep, TMPDIR, 'reports'))

RUN_URL_PATH = '/run'
MODULE_URL_PATH = '/module'
USER_URL_PATH = '/user'

CLOUD_NAME_ABIQUO = 'abiquo'
CLOUD_NAME_OPENSTACK = 'openstack'
CLOUD_NAME_EC2 = 'ec2'
CLOUD_NAME_STRATUSLAB = 'stratuslab'
CLOUD_NAME_CLOUDSIGMA = 'cloudsigma'
CLOUD_NAME_PHYSICALHOST = 'physicalhost'
CLOUD_NAME_LOCAL = 'local'

SUPPORTED_PLATFORMS_BY_DISTRO = {'debian_based' : ('ubuntu',),
                                 'redhat_based' : ('fedora', 'redhat', 'centos')}
SUPPORTED_PLATFORMS = [y for x in SUPPORTED_PLATFORMS_BY_DISTRO.values() for y in x]

def configureLogger():
    filename=os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),'slipstream.log')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename=filename)

def execute(commandAndArgsList, **kwargs):
    wait = not kwargs.get('noWait', False)

    if kwargs.has_key('noWait'):
        del kwargs['noWait']

    withStderr = kwargs.get('withStderr', False)
    withStdOutErr = kwargs.get('withOutput', False)
    # Getting stderr takes precedence on getting stdout&stderr.
    if withStderr:
        kwargs['stderr'] = subprocess.PIPE
        withStdOutErr = False
    if kwargs.has_key('withStderr'):
        del kwargs['withStderr']

    if withStdOutErr:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.STDOUT
        kwargs['close_fds'] = True
    if kwargs.has_key('withOutput'):
        del kwargs['withOutput']

    if isinstance(commandAndArgsList, list):
        _cmd = ' '.join(commandAndArgsList)
    else:
        _cmd = commandAndArgsList

    printDetail('Calling: %s' % _cmd, kwargs)

    if isinstance(commandAndArgsList, list) and kwargs.get('shell', False) == True:
        commandAndArgsList = ' '.join(commandAndArgsList)

    process = subprocess.Popen(commandAndArgsList, **kwargs)

    if wait:
        process.wait()

    if withStderr:
        return process.returncode, process.stderr.read()
    elif withStdOutErr:
        return process.returncode, process.stdout.read()
    else:
        return process.returncode

def removeLogger(handler):
    logger = logging.getLogger()
    logger.removeHandler(handler)

def redirectStd2Logger():
    configureLogger()
    sys.stderr = StdOutWithLogger('stderr')
    sys.stdout = StdOutWithLogger('stdout')

def resetStdFromLogger():
    sys.stdout = sys.stdout._std
    sys.stderr = sys.stderr._std

def redirectStd2File(filename):
    sys.stderr = StdOutWithFile(filename)
    sys.stdout = StdOutWithFile(filename)

def resetStdFromFile():
    sys.stdout = sys.stdout._stdout
    sys.stderr = sys.stderr._stderr

def whoami():
    return sys._getframe(1).f_code.co_name

class StdOutWithFile(object):
    def __init__(self, filename):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        self.fh = file(filename, 'w')
    
    def __del__(self):
        self.flush()
        self.fh.close()

    def writelines(self, msgs):
        # Test if msgs is a list or not
        try:
            msgs.append('')
        except AttributeError:
            # It's probably a string, so we write it directly
            self.write(msgs + '\n')
            return
        for msg in msgs:
            self.write(msg)
        self.flush()

    def write(self, _string):
        _string = unicode(_string).encode('utf-8')
        self._stdout.write(_string)
        self.fh.write(_string)
        self.flush()

    def flush(self):
        self._stdout.flush()
        self.fh.flush()
        
class StdOutWithLogger:
    def __init__(self, std):
        if std == 'stdout':
            self._std = sys.stdout
            self.logType = 'out'
        elif std == 'stderr':
            self._std = sys.stderr
            self.logType = 'err'
        else:
            raise ValueError('Unknown std type: %s' % std)

    def writelines(self, msgs):
        # Test if msgs is a list or not
        try:
            msgs.append('')
        except AttributeError:
            # It's probably a string, so we write it directly
            self.write(msgs + '\n')
            return
        for msg in msgs:
            self.write(msg)
        return

    def write(self, string):
        _string = unicode(string).encode('utf-8')
        self._std.write(_string)
        if string == '.':
            return
        if self.logType == 'out':
            logging.info(_string)
        else:
            logging.error(_string)
        return

    def flush(self):
        self._std.flush()

def getHomeDirectory():
    if (sys.platform == "win32"):
        if (os.environ.has_key("HOME")):
            return os.environ["HOME"]
        elif (os.environ.has_key("USERPROFILE")):
            return os.environ["USERPROFILE"]
        else:
            return "C:\\"
    else:
        if (os.environ.has_key("HOME")):
            return os.environ["HOME"]
        else:
            # No home directory set
            return ""

def getConfigFileName():
    ''' Look for the configuration file in the following order:
        1- local directory
        2- installation location
        3- calling module location
    '''
    filename = 'slipstream.client.conf'
    configFilename = os.path.join(os.getcwd(),filename)
    if os.path.exists(configFilename):
        return configFilename
    configFilename = os.path.join(getInstallationLocation(),filename)
    if not os.path.exists(configFilename):
        configFilename = os.path.join(os.path.dirname(sys.argv[0]),filename)
    if not os.path.exists(configFilename):
        raise Exceptions.ConfigurationError('Failed to find the configuration file: ' + configFilename)
    return configFilename

def getInstallationLocation():
    ''' Look for the installation location in the following order:
        1- SLIPSTREAM_HOME env var if set
        2- Default target directory, if exists (/opt/slipstream/src)
        3- Base module: __file__/../../.., since the util module is namespaced
    '''
    slipstreamDefaultDirName = os.path.join(os.sep,'opt','slipstream','client','src')
    # Relative to the src dir.  We do this to avoid importing a module, since util
    # should have a minimum of dependencies
    slipstreamDefaultRelativeDirName = os.path.join(os.path.dirname(__file__),'..','..','..')
    if os.environ.has_key('SLIPSTREAM_HOME'):
        slipstreamHome = os.environ['SLIPSTREAM_HOME']
    elif os.path.exists(slipstreamDefaultDirName):
        slipstreamHome = slipstreamDefaultDirName
    else:
        slipstreamHome = slipstreamDefaultRelativeDirName
    return slipstreamHome

def uuid():
    '''Generates a unique ID.'''
    return str(uuidModule.uuid4())

def printDetail(message, verboseLevel=1, verboseThreshold=1):
    if verboseLevel >= verboseThreshold:
        printAndFlush('\n    %s\n' % message)

def _printDetail(message, kwargs={}):
    verboseLevel = _extractVerboseLevel(kwargs)
    verboseThreshold = _extractVerboseThreshold(kwargs)
    printDetail(message, verboseLevel, verboseThreshold)

def _extractVerboseLevel(kwargs):
    return _extractAndDeleteKey('verboseLevel', 0, kwargs)

def _extractVerboseThreshold(kwargs):
    return _extractAndDeleteKey('verboseThreshold', 2, kwargs)

def _extractAndDeleteKey(key, default, dict):
    value = default
    if key in dict:
        value = dict[key]
        del dict[key]
    return value

def printAction(message):
    length = len(message)
    padding = 4*'='
    line = (length + 2*len(padding) + 2)*'='
    _message = padding + ' %s ' % message + padding
    printAndFlush('\n%s\n%s\n%s\n' % (line, _message, line))

def printStep(message):
    printAndFlush('\n==== %s\n' % message)

def printAndFlush(message):
    if PRINT_TO_STDERR_ONLY:
        output = sys.stderr
    else:
        output = sys.stdout
    output.flush()
    print >> output, message,
    output.flush()

def printError(message):
    sys.stdout.flush()
    sys.stderr.flush()
    print >> sys.stderr, 'ERROR: %s' % message
    sys.stdout.flush()
    sys.stderr.flush()

def assignAttributes(obj, dictionary):
    for key, value in dictionary.items():
        setattr(obj, key, value)

def loadModule(moduleName):
    namespace = ''
    name = moduleName
    if name.find('.') != -1:
        # There's a namespace so we take it into account
        namespace = '.'.join(name.split('.')[:-1])

    return __import__(name, fromlist=namespace)

def parseConfigFile(filename, preserve_case=True):
    parser = SafeConfigParser()
    if preserve_case:
        parser.optionxform = str
    parser.read(filename)
    return parser

def toTimeInIso8601(_time):
    "Convert int or float to time in iso8601 format."
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(_time))

def toTimeInIso8601NoColon(_time):
    return toTimeInIso8601(_time).replace(':', '')

def filePutContent(filename, data):
    _printDetail('Creating file %s with content: \n%s\n' % (filename, data))
    fd = open(filename, 'wb')
    fd.write(data)
    fd.close()

def filePutContentInTempFile(data):
    _, filename = tempfile.mkstemp()
    filePutContent(filename, data)
    return filename

def fileAppendContent(filename, data):
    fd = open(filename, 'a')
    fd.write(data)
    fd.close()

def fileGetContent(filename):
    fd = open(filename, 'rb')
    content = fd.read()
    fd.close()
    return content

def importETree():
    try:
        from lxml import etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # Python 2.5
                import xml.etree.cElementTree as etree
            except ImportError:
                try:
                    # normal cElementTree install
                    import cElementTree as etree
                except ImportError:
                    try:
                        # normal ElementTree install
                        import elementtree.ElementTree as etree
                    except ImportError:
                        raise Exception("Failed to import ElementTree from any known place")
    return etree

def removeASCIIEscape(data):
    if hasattr(data, 'replace'):
        return data.replace('\x1b', '')
    else:
        return data

def _waitMachineNetworkUpOrAbort(host, instanceId, timeout=60):
    host_coords = "(id=%s, ip=%s)" % (host, instanceId)
    printStep("Waiting for machine network to start: %s" % host_coords)
    if not waitUntilPingOrTimeout(host, timeout):
        msg = 'Unable to ping VM in %i seconds: %s' % (timeout, host_coords)
        raise Exceptions.ExecutionException(msg)

def waitUntilPingOrTimeout(host, timeout, ticks=True, stdout=None, stderr=None):
    if not stdout:
        stdout = open('/dev/null', 'w')
    if not stderr:
        stderr = open('/dev/null', 'w')

    start = time.time()
    hostUp = False
    while not hostUp:
        if ticks:
            sys.stdout.flush()
            sys.stdout.write('.')
        hostUp = ping(host, stdout=stdout, stderr=stderr)
        sleep(1)

        if time.time() - start > timeout:
            if ticks:
                sys.stdout.flush()
                sys.stdout.write('\n')
            return False

    if ticks:
        sys.stdout.flush()
        sys.stdout.write('\n')
    return hostUp

def ping(host, timeout=5, number=1, **kwargs):
    p = subprocess.Popen(['ping', '-q', '-c', str(number), host], **kwargs)
    p.wait()
    success = (p.returncode == 0)
    return success

def sleep(seconds):
    time.sleep(seconds)

def _getSecureHostPortFromUrl(endpoint):
    scheme, netloc, _, _, _, _ = urllib2.urlparse.urlparse(endpoint)
    if scheme == 'http' or not scheme:
        secure = False
    elif scheme == 'https':
        secure = True
    else:
        raise ValueError('Unknown scheme %s' % scheme)
    if ":" in netloc:
        host, port = netloc.split(':')
    else:
        host = netloc
        port = None
    return secure, host, port
