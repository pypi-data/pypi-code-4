# -*- coding: utf-8 -*-

import os
from multiprocessing import Process, freeze_support
from signal import SIGINT
import logging
from squeezeui.controllers import mainwindow
from squeezeui.controllers.config import setuplogging, audioplayers

setuplogging()

def childProcess(main_pid, *args):
    mainwindow.serve_forever()
    logging.debug('kill process %r from %r', main_pid, os.getpid())
    os.kill(main_pid, SIGINT)

window = Process(target=childProcess, args=(os.getpid() ,))

# merge default config with auto-discovered config.
config = {}

def _merge_config():
    mainwindow.config.update(config)
    mainwindow.discover_server()
    config.update(mainwindow.config)
    
def start():
    """ Start player in childprocess. """
    if os.name == 'nt':
        freeze_support()
    _merge_config()
    window.start()

def stop():
    """ Stop player in childprocess """
    window.join()

def start_blocking():
    """ Start player in mainprocess """
    _merge_config()
    mainwindow.serve_forever()

def start_blocking_with_audioplayer():
    """ Start player in mainprocess and start
        a audioplayer in subprocess.
    """
    import subprocess
    import shlex
    
    audioplayerprocess = None
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
    try:
        _merge_config()
        # try to start local players
        for name, cmdline in audioplayers.items():
            try:
                _args = shlex.split(cmdline.format(player=config))
                audioplayerprocess = subprocess.Popen(_args, startupinfo=startupinfo)
                start_blocking()
                break
            except FileNotFoundError:
                pass
        else:
            start_blocking()
            
    except KeyboardInterrupt:
        pass
    
    if audioplayerprocess:
        audioplayerprocess.terminate()
