'''
Created on Apr 28, 2013

:author: chen
'''

import logging
import os
import sys


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


@run_once
def sharedLogger():
    procID = os.getpid()
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    logger = logging.getLogger("TradingMachine")
    logger.handlers = []    # Clear standard io handler.
    logger.setLevel(logging.DEBUG)

    streamhandler = logging.StreamHandler(sys.stdout)
    streamhandler.setFormatter(formatter)
    streamhandler.setLevel(logging.INFO)

    directory = os.path.join(os.path.expanduser("~"), "Library", "Logs", "TradingMachine")
    if not os.path.exists(directory):
        os.makedirs(directory)
    filehandler = logging.FileHandler(filename=os.path.join(directory, "TradingMachine_" + str(procID) + ".log"))
    filehandler.setFormatter(formatter)
    filehandler.setLevel(logging.DEBUG)

    logger.addHandler(streamhandler)
    logger.addHandler(filehandler)
    return logger

logger = sharedLogger()
