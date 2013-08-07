import logging
import subprocess
import socket
import atexit
import random

# TODO: we shouldnt need jpype, just better python subprocess control..
import jpype

from clover import get_package_resource


PORT = random.randint(10000,60000)

SERVICE_STARTED = False

# jpype is preferred for greater control of the jvm
JPYPE_JVM = True

# Used to set java maximum heap size (-Xmx). In MB.
MAXIMUM_HEAP = 900


CLOVER_JAR = get_package_resource('jars/clover.jar')

class Service(object):
    """ Manages the clover/compiler service.
    """
    port = PORT
        
    started = False
    
    @classmethod
    def start(self):
        global SERVICE_STARTED

        if SERVICE_STARTED:
            return True
        
        logging.debug('Starting jvm %s', CLOVER_JAR)

        if JPYPE_JVM:    
            jvmpath = jpype.getDefaultJVMPath()
            arg = "-Djava.class.path=%s" % CLOVER_JAR
            logging.info('Running clover server, %s %s', arg, jvmpath)
            jpype.startJVM(jvmpath, '-Xmx%sm' % MAXIMUM_HEAP, arg)
            logging.info('Starting clover service...')
            server = jpype.JPackage("clover").Service
            server.main([str(self.port)])
        else:
            cmd = ['java', '-Xmx%sm' % MAXIMUM_HEAP, '-jar', CLOVER_JAR, str(PORT)]
            proc = subprocess.Popen(cmd)
            atexit.register(proc.terminate)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                try:
                    s.connect(('127.0.0.1', PORT))
                    s.shutdown(2)
                    print "Server opened: port " + str(PORT)
                    break
                except:
                    pass
            

        SERVICE_STARTED = True

    service_class = None
        
    @classmethod
    def stop(self):
        jpype.shutdownJVM()
        self.started = False
        

def launch_gateway(port=0, jarpath="", classpath="", javaopts=[],
        die_on_exit=False):
    """Launch a `Gateway` in a new Java process.

    :param port: the port to launch the Java Gateway on.  If no port is
        specified then an ephemeral port is used.
    :param jarpath: the path to the Py4J jar.  Only necessary if the jar
        was installed at a non-standard location or if Python is using
        a different `sys.prefix` than the one that Py4J was installed
        under.
    :param classpath: the classpath used to launch the Java Gateway.
    :param javaopts: an array of extra options to pass to Java (the classpath
        should be specified using the `classpath` parameter, not `javaopts`.)
    :param die_on_exit: if `True`, the Java gateway process will die when
        this Python process exits or is killed.

    :rtype: the port number of the `Gateway` server.
    """
    if not jarpath:
        jarpath = find_jar_path()

    # Fail if the jar does not exist.
    if not os.path.exists(jarpath):
        raise Py4JError("Could not find py4j jar at {0}".format(jarpath))

    # Launch the server in a subprocess.
    classpath = os.pathsep.join((jarpath, classpath))
    command = ["java", "-classpath", classpath] + javaopts + \
              ["py4j.GatewayServer"]
    if die_on_exit:
        command.append("--die-on-broken-pipe")
    command.append(str(port))
    logger.debug("Lauching gateway with command {0}".format(command))
    proc = Popen(command, stdout=PIPE, stdin=PIPE)

    # Determine which port the server started on (needed to support
    # ephemeral ports)
    _port = int(proc.stdout.readline())
    return _port


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    server = Service()
    server.start()