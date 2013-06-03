# @package jobsubmission

# Imports
import threading, subprocess
from multiprocessing import Process, Pipe
import datetime, time, os

import cherrypy
import vispa
import vispa.rpc
#from analysis import *
#from vispa.plugins.rpc import RpcProcess
from inspect import getmembers

import logging

# @class job.JobPool
class JobPool(object):

    def __init__(self, owner):
        self.owner = owner
        self.__batchManager = {}

        self.__defaultmanager = "LocalBatchManager"

        if vispa.config.has_section('BatchSystem'):
            if vispa.config.has_option('BatchSystem', 'manager'):
                 readout = vispa.config.get('BatchSystem', 'manager')
                 if readout in ["local", "LocalBatchManager"]:
                     self.__defaultmanager = "LocalBatchManager"
                 elif readout in ["grid", "GridBatchManager"]:
                     self.__defaultmanager = "GridBatchManager"
                 elif readout in ["lsf", "LSFBatchManager"]:
                     self.__defaultmanager = "LSFBatchManager"
                 elif readout in ["hpc", "LSFBatchManager"]:
                     self.__defaultmanager = "LSFBatchManager"
                 elif readout in ["condor", "CondorBatchManager"]:
                     self.__defaultmanager = "CondorBatchManager"
                 else:
                     logging.getLogger("system.batchsystem").info("Could not recognize the shortcut of the default manager in vispa.ini configuration. Use one out of '%s' or use the exact name, e.g. 'CondorBatchManager' (without quotation marks)." % ("'local','grid','lsf','hpc','condor'"))

        logging.getLogger("system.batchsystem").info("Default batchsystem is '%s' ." % (self.__defaultmanager))
        self._batchmanagerOutputFolder = "/tmp"

    def setAvailableBatchManager(self, availableManager):
        self.availableManager = availableManager

#    @cherrypy.expose
#    @cherrypy.tools.user()
#    @cherrypy.tools.workspace()
    def _manager(self, manager=None):

        if not manager:
            manager = self.__defaultmanager

        try:
            m = vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, "BatchSystemManager." + manager + "." + manager + "." + manager)
            return m
        except Exception, e:
                vispa.log_exception()
                raise Exception("Couldn't get rpc instance of BatchSystemManager! <br />Reason: %s" % str(e))

        return False


    def getJobData(self, batchManagerFolder, manager=None):
        '''returns information about all current jobs as list of 
        dictionaries.'''

        data = []
        bm = self._manager(manager)

        if not manager:
            manager = self.__defaultmanager

        #different folders for condor, local etc.
        bm.setDataPath(batchManagerFolder + "/" + manager)
        bm.update()

        #job history: includes initial load of all jobs that have been already written to disk
        bm.loadJobList()

        jobs = bm.getJobList()
        for jobid in jobs:
            job = jobs[jobid]
            submissiontime = job["SubmissionTime"]
            finishedtime = job["FinishedTime"] if "FinishedTime" in job else submissiontime
            if finishedtime != submissiontime:
                runtime = finishedtime - submissiontime
            else:
                runtime = 0
            runtime = str(datetime.timedelta(0, runtime))
            submissiontime = str(datetime.datetime.fromtimestamp(submissiontime))
            finishedtime = str(datetime.datetime.fromtimestamp(finishedtime))
            data.append({'jobid': jobid, 'command': job["Command"], 'status': job["Status"],
                         'submissiontime': submissiontime, 'finishedtime': finishedtime,
                         'runtime': runtime, "group": job["group"]})

        return data

    def getJobOutput(self, jobid, manager=None):
        output = self._manager(manager).getJobOutputData(jobid)
        return output

    def getJobError(self, jobid, manager=None):
        error = self._manager(manager).getJobErrorData(jobid)
        return error

    def getJobCommand(self, jobid, manager=None):
        command = self._manager(manager).getJobCommand(jobid)
        return command

    def restartJob(self, jobid, manager=None):
        self._manager(manager).restartJob(jobid)

    def removeJob(self, jobid, manager=None):
        self._manager(manager).removeJob(jobid)

    def stopJob(self, jobid, manager=None):
        self._manager(manager).stopJob(jobid)

    def submit(self, command, batchManagerFolder, manager=None, preExecutionScriptText=None, postExecutionScriptText=None, outputPath=None):
        '''In case of using RPC and the BatchManager, there's no use of
        managing the job with the JobPool. Instead the job is just submitted 
        to the BatchManager and the status is polled in the run loop.'''

        logging.getLogger("system.batchsystem").info("submit remote")

        logging.getLogger("system.batchsystem").info("Add job with command %s" % command)

        if not manager:
            manager = self.__defaultmanager

        bm = self._manager(manager)
        bm.setDataPath(batchManagerFolder + "/" + manager)

        _preExecutionScriptText = preExecutionScriptText
        _postExecutionScriptText = postExecutionScriptText

        if _preExecutionScriptText == None:
            _preExecutionScriptText = ""

        if _postExecutionScriptText == None:
            _postExecutionScriptText = ""

        _jobOptions = None

        jobid = bm.addJob(command, _preExecutionScriptText, _postExecutionScriptText, _jobOptions)
        logging.getLogger("system.batchsystem").info("Job '%s' successfully submitted to batch manager" % jobid)

    def _getBatchManagerOutputFolder(self):
        return self.__batchManagerOutputFolder