#!/usr/bin/python
# -*- coding: utf-8 -*-
# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python testdaemon.py start

#standard python libs
import logging
import time

#Indexador
from app import main

#third party libs
from daemon import runner
import ConfigParser

def setconfig():
    """Função que conecta o modulo ao arquivo de configurações"""
    
    config = ConfigParser.ConfigParser()
    config.read('development.ini')
    domain = config.get('LBIndex', 'domain')
    elastic = config.get('LBIndex', 'elastic')
    tempo = int(config.get('LBIndex', 'tempo'))

    stdin_path = config.get('Daemon', 'stdin_path')
    stdout_path = config.get('Daemon', 'stdout_path')
    stderr_path = config.get('Daemon', 'stderr_path')
    pidfile_path = config.get('Daemon', 'pidfile_path')
    logfile_path = config.get('Daemon', 'logfile_path')
    pidfile_timeout = int(config.get('Daemon', 'pidfile_timeout'))
    return domain, elastic, tempo, stdin_path, stdout_path, stderr_path, pidfile_path, logfile_path, pidfile_timeout

class App():
   
    def __init__(self):
        self.stdin_path = stdin_path
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path
        self.pidfile_path =  pidfile_path
        self.pidfile_timeout = pidfile_timeout
           
    def run(self):
        while True:
            logger.info ('Iniciando rotina de indexação')
            main(domain, elastic)
            time.sleep(tempo)
(domain, elastic, tempo, stdin_path, stdout_path, stderr_path, pidfile_path, logfile_path, pidfile_timeout) = setconfig()
app = App()
logger = logging.getLogger("LBIndex")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(logfile_path)
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()