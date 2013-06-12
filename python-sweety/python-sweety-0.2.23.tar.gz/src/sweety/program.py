#!/usr/bin/env python
'''
sweety.program

@author: Yunzhi Zhou (Chris Chou)
'''

import atexit
import datetime
import os
import argparse
import logging
import multiprocessing
import sys
import textwrap
import traceback
import types
import shlex
import signal

import setproctitle

import conf
from conf import config
from conf import version
import log
import lock
import valuebag


__all__ = ['Program', 'UnitTestProgram', 'main', 'unittest_main', 'SINGLETON_NOT_SINGLETON', 'SINGLETON_EXIT', 'SINGLETON_WAIT']

_program = None

def get_program():
    global _program
    
    return _program

class Program(object):
    
    
    EXITCODE_INITIALIZATION_FAILURE = (101, 'Failed to initialize the program.')
    EXITCODE_MAIN_FAILURE = (102, 'Uncaught exception in the main program.')
    EXITCODE_FINALIZATION_FAILURE = (103, 'Failed to finalize the program.')
    EXITCODE_MULTIPLE_INSTANCE = (110, 'Another instance is running.')
    
    def __init__(self, name = os.path.basename(sys.argv[0])):
        self.logger = log.get_logger(self)
        
        self.prog_info = conf.ValueBag()
        self.prog_info.START_TIMESTAMP = datetime.datetime.now()
        self.prog_info.PROG_NAME = name
        self.prog_info.PROG_VERSION = version.VERSION
        self.prog_info.PROG_PID = os.getpid()
        #self.prog_info.PID_FILE = os.environ[config.INV_PIDFILE]
        #self.prog_info.SINGLETON = singleton
        
        os.environ[config.ENV_PROGRAM] = name

        self.prog_args = valuebag.ValueBag()
        
        self.argparser = argparse.ArgumentParser()
        self.argparser.formatter_class = argparse.RawDescriptionHelpFormatter
        self.argparser.description = self.prog_info.PROG_NAME
        self.argparser.epilog = textwrap.dedent('''
            All rights reserved (c) Copy right.
            Version: %s
            
        ''' % self.prog_info.PROG_VERSION)
        self.argparser.add_argument(
                '-v', '--verbose', dest = 'VERBOSE', action = 'store_true',
                default = False,
                help = 'turn on verbose mode.'
                                    )
        self.argparser.add_argument(
                '-V', '--version', dest = 'VERSION', action = 'store_true',
                default = False,
                help = 'show version.')

                        
    def initialize(self):
        pass
    
    def run(self):
        pass
    
    def finalize(self):
        pass
    
    def duration(self):
        return datetime.datetime.now() - self.prog_info.START_TIMESTAMP
        
    def set_status(self, message):
        setproctitle.setproctitle('%s [%s]' % (' '.join(sys.argv), message))
        
    def exit(self, exitcode = 0,  last_message = ''):
        duration = self.duration()
        if not exitcode:
            if last_message:
                self.logger.info('%s - [Program exits. Status: %d, Duration: %s]' % (last_message, exitcode, duration))
            else:
                self.logger.info('[Program exits. Status: %d, Duration: %s]' % (exitcode, duration))
        else:
            if last_message:
                self.logger.critical('%s - [Program exits. Status: %d, Duration: %s]' % (last_message, exitcode, duration))
            else:
                self.logger.critical('[Program exits. Status: %d, Duration: %s]' % (exitcode, duration))
                
        logging.shutdown()
        
        _terminate_logging_process()
        
        sys.exit(exitcode)
        
    
    def print_help(self):
        self.argparser.print_help()
    
    def print_version(self):
        print 'Verison: %s' % self.prog_info.PROG_VERSION
    
    def send_error(self, code, message, errinfo):
        pass
    
        
def _print_config(config, log):
    for k in config:
        if k != k.upper():
            continue

        v = getattr(config, k)
        if isinstance(v, (types.ModuleType, types.FunctionType)):
            continue

        log.info(' ++++ %s: %s' % (k, str(v)))

SINGLETON_NOT_SINGLETON = 0
SINGLETON_WAIT = 1
SINGLETON_EXIT = 2

_logging_process = None


def get_logging_process():
    global _logging_process
    
    return _logging_process

def _terminate_logging_process():
    pro = get_program()
    if pro.prog_info.PROG_PID == os.getpid():
        p = get_logging_process()
        if p:
            logger = log.get_logger('_exit')
            logger.info('Logging process exits.')
            p.join()
            
            global _logging_process
            _logging_process = None
            #print 'terminate'
            
#        if os.environ.has_key(config.ENV_LOGGER_SOCKFILE):
#            sockfile = os.environ[config.ENV_LOGGER_SOCKFILE]
#            try:
#                os.remove(sockfile)
#            except:
#                pass                
#            
#def _delete_singleton_file():
#    if os.environ[config.ENV_PID] == str(os.getpid()):
#        if os.environ.has_key(config.ENV_PIDFILE):
#            pidfile = os.environ[config.ENV_PIDFILE]
#            if os.path.isfile(pidfile):
#                os.remove(pidfile)

def main(prog_or_class, singleton = SINGLETON_NOT_SINGLETON, multiproc_logging = False):
    '''
    main(progclass) -> status code
    
    Wraps a main function, handling common tasks before proceeding specific logic.
    
    @param progclass: the class implements following functions:
        help() - displays help information.
        version() - displays version information.
        main() - the program entry.
    '''
    start_timestamp = datetime.datetime.now()
        
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    os.environ[config.ENV_PID] = str(os.getpid())

    # hack
    if '-v' in sys.argv or '--verbose' in sys.argv:
        os.environ[config.ENV_VERBOSE] = '1'
    
    if multiproc_logging:
        os.environ[config.ENV_LOGGER_SOCKFILE] = os.path.join(
                                                    config.TMP_DIR,
                                                    '%s.%d.logger.sockfile' % (os.path.basename(sys.argv[0]), os.getpid()) 
                                                     )
        global _logging_process
        assert _logging_process is None
        
        logcond = multiprocessing.Condition()
        logcond.acquire()
        _logging_process = multiprocessing.Process(target = log.multiproc_logger_main, args = (logcond,))
        _logging_process.start()
        logcond.wait()
        logcond.release()
        #print 'after'
        #_logging_process.daemon()
        os.environ[config.ENV_LOGGER_PID] = str(_logging_process.ident)
#        log.get_logger = log.get_remote_logger
        log.setup_root_logger(True)
        atexit.register(_terminate_logging_process)
    else:
        log.setup_root_logger(False)   
        
        #atexit.register(_terminate_logging_process)

    #root = log.get_logger('root')
    logger = log.get_logger('main')
    #logger.setLevel(logging.WARNING)
                    
    if not os.environ.has_key(config.ENV_VIRTUAL_ENV):
        logger.fatal('Virtual environment is not found.')
        sys.exit(100)

    logger.info('Program started, command line [%s]' % ' '.join(sys.argv))

    if len(sys.argv) >= 3 and sys.argv[len(sys.argv) - 2] == '--':
        try:
            with open(sys.argv[len(sys.argv) - 2]) as f:
                extra = f.read()
            sys.argv[(len(sys.argv) - 2):] = shlex.split(extra) 
        except:
            pass

    logger.info('Expanded command line [%s]' % ' '.join(sys.argv))

    logger.info('Environment variables:\n%s' % '\n'.join(
        [' +++ %s: %s' % (k, os.environ[k]) for k in os.environ]
        ))

    logger.info('Printing config:')
    _print_config(config, logger)


    if callable(prog_or_class):
        prog = prog_or_class()
    else:
        prog = prog_or_class
    global _program
    _program = prog
    prog.prog_info.START_TIMESTAMP = start_timestamp

    if singleton:
        lockfile = os.path.join(config.TMP_DIR, '%s.%s.%s.pid' % (
                                                              os.path.realpath(os.path.dirname(sys.argv[0])).replace('/', '__'),
                                                              os.path.basename(sys.argv[0]),
                                                              prog.__class__.__name__ 
                                                              ))
        os.environ[config.ENV_PIDFILE] = lockfile

        #atexit.register(_delete_singleton_file)
        
        lockfp = open(lockfile, 'w')
        lockfp.write(str(os.getpid()))
        lockobj = lock.FileWriteLock(lockfp)
        if singleton == SINGLETON_WAIT:
            lockobj.lock()
        elif singleton == SINGLETON_EXIT:
            if not lockobj.trylock():
                prog.exit(*prog.EXITCODE_MULTIPLE_INSTANCE)
                

    try:
        logger.info('Initializing program.')
        prog.initialize()
    except SystemExit:
        pass
    except:
        errinfo = traceback.format_exc()
        logger.critical(errinfo)
        
        prog.exit(*prog.EXITCODE_INITIALIZATION_FAILURE)

    prog.prog_args = valuebag.ValueBag(vars(prog.argparser.parse_args()))

    ret = 0
    errinfo = None
    exit_code = 0
    exit_message = ''
    try:
        logger.info('Entering main program.')
        ret = prog.run()
        ret = 0 if ret is None else ret
        if isinstance(ret, (list, tuple)):
            exit_code, exit_message = ret
        elif isinstance(ret, bool):
            exit_code = not ret
        else:
            exit_code = int(ret)
    except SystemExit, e:
        exit_code = e.code
    except BaseException, e:
        errinfo = traceback.format_exc()
        logger.critical(errinfo)
        
        exit_code, exit_message = prog.EXITCODE_MAIN_FAILURE
        exit_message = '%s: %s' % (e.__class__.__name__, str(e) or '<No message>')
        
    try:
        logger.info('Finalizing program.')
        prog.finalize()
    except SystemExit, e:
        exit_code = e.code
    except BaseException, e:
        errinfo = traceback.format_exc()
        logger.critical(errinfo)
        
        exit_code, exit_message = prog.EXITCODE_FINALIZATION_FAILURE
        exit_message = '%s: %s' % (e.__class__.__name__, str(e) or '<No message>')
        
    if exit_code:
        try:
            logger.info('Sending error notification.')
            prog.send_error(exit_code, exit_message, errinfo)
        except:
            logger.error(traceback.format_exc())
            logger.error('Cant send notification.')
            
    prog.exit(exit_code, exit_message)
    
    
class UnitTestProgram(Program):
    def __init__(self):
        super(UnitTestProgram, self).__init__('unittest')
        
    def run(self):
        import unittest
        
        unittest.main()
        
def unittest_main():
    main(UnitTestProgram)


