# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa
import vispa.rpc
import logging
from vispa.controller import AbstractController

class JobmanagementController(AbstractController):

    def __init__(self, extension):
        AbstractController.__init__(self)
        setattr(self, 'extension', extension)

        # default paths
        self.__batchManagerOutputFolder = None

        # translated paths
        self.__batchManagerOutputFolder_vfs = {}

    @cherrypy.expose
    def data(self):
        return 'data'

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.workspace()
    def getCommandLineDesigner(self):
        try:
            cmdLineDesigner = vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, "BatchSystemManager.Core.CommandLineDesigner.CommandLineDesigner")

            return cmdLineDesigner
        except Exception, e:
            return self.fail("Couldn't get the CommandLineDesigner RPC process! <br />Reason: %s" % str(e))

        return False

    """START: Job Submission FORM ajax requests"""

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def resetCommandLineDesigner(self, extid):
        try:
            self.getCommandLineDesigner().reset()

            return self.success({"success": True})
        except Exception, e:
            return self.fail("Couldn't reset the CommandLineDesigner RPC process! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.workspace()
    def updateValue(self, bm_name, variable, value):
        try:
            if variable == "MaxRunning":
                pass

            return self.success({{"success": True}})
        except Exception, e:
            return self.fail("Couldn't load the Analysis!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getAvailableBatchManager(self):
        try:
            bm = vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, "BatchSystemManager.Core.BatchSystemManagerAvailability.BatchSystemManagerAvailability")

            bm_dict = {}

            for entry in bm.checkSystemAvailability():
                if not entry in bm_dict:
                    bm_dict[entry] = {"name":entry, "description":""}

            descriptions = bm.getDescriptions()
            for entry in descriptions:
                if entry in bm_dict:
                    bm_dict[entry]["description"] = descriptions[entry]

            returnValues = []
            for key in bm_dict:
                returnValues.append(bm_dict[key])

            return {"data":returnValues, "success":True}
        except Exception, e:
            return self.fail("Couldn't load available batchmanager!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.workspace()
    def getBatchManagerConfiguration(self, extid, batchmanager):
        try:
            template = cherrypy.engine.publish("lookup_template", batchmanager + "Configuration.html", "", "jobmanagement").pop()

            bm = vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, "BatchSystemManager." + batchmanager + "." + batchmanager + "." + batchmanager)
            bm.update()
            contentDict = {}

            if batchmanager == "CondorBatchManager":
                userpriorities = bm.getUserPriorities()
                content = {}
                content["availableCores"] = str(bm.getAvailableCores())
                content["coresClaimedByOwner"] = str(bm.getCoresClaimedByOwner())
                content["coresClaimedByCondor"] = str(bm.getCoresClaimedByCondor())
                content["unclaimedCores"] = str(bm.getUnclaimedCores())
                contentDict = {"extid": extid, "batchmanager":batchmanager, "userpriorities":userpriorities, "availableCores":content["availableCores"], "coresClaimedByOwner":content["coresClaimedByOwner"], "coresClaimedByCondor":content["coresClaimedByCondor"], "unclaimedCores":content["unclaimedCores"]}
            elif batchmanager == "LocalBatchManager":
                contentDict = {"extid": extid, "batchmanager":batchmanager, "maxRunning": bm.getMaxRunning()}
            elif batchmanager == "LSFBatchManager":
                contentDict = {"extid": extid, "batchmanager":batchmanager}
            elif batchmanager == "GridBatchManager":
                contentDict = {"extid": extid, "batchmanager":batchmanager}
            else:
                contentDict = {"extid": extid, "batchmanager":batchmanager}

            return template.render(**contentDict)

        except Exception, e:
            return self.fail("Couldn't load batchmanager configuration!<br />Reason: %s" % str(e))

    """END: Job Submission FORM ajax requests"""

    """START: Job DESIGNER FORM ajax requests"""


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def readfile(self, extid, path):
        logging.getLogger("system.extensions.jobsubmssion").debug("read file with virtual path='%s'" % (str(path)))

        try:
            # vfs = self._get_vfs_instance(uname)
            # content, msg = vfs.getFileContent(uname, path)

            return self.success({"success": True,
                                 # "content":content.data
                                 "content":"Couldn't read file .. fix filesystem"
                                 })
        except Exception, e:
            return self.fail("Couldn't read the file! <br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    # @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def savefile(self, extid, path, content):
#    def savefile(self, data):
#        extid = data["extid"]
#        path = data["path"]
#        content = data["content"]
        logging.getLogger("system.extensions.jobsubmssion").debug("save file to virtual path='%s'" % (str(path)))

        try:
            content = eval(content)
            success = False
            # FIXME#success, msg = vfs.saveFileContent(uname, str(path), xmlrpclib.Binary(content.encode('utf-8')))
            if not success:
                raise Exception(msg)

            return self.success({'msg': msg})
        except Exception, e:
            return self.fail("Couldn't save the file! <br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def loadjobfile(self, extid, path):
        logging.getLogger("system.extensions.jobsubmssion").debug("load CommandLine from file with virtual path='%s'" % (str(path)))

        try:
#            vfs = self._get_vfs_instance(uname)
#            realpath = vfs.translateVirtualPath(uname, path)

            logging.getLogger("system.extensions.jobsubmssion").debug("Resolved virtual path='%s' to path='%s'" % (str(path), str(realpath)))
            self.getCommandLineDesigner().loadFromFile(path)
            # self.getCommandLineDesigner().loadFromFile(realpath)

            return self.success({"success": True,
                                 "optionList":self.getlistofoptions(extid)["optionList"],
                                 "parameterRangeList":self.getlistofparameterranges(extid)["parameterRangeList"],
                                 "optionDecoratorList":self.getlistofoptiondecorators(extid)["optionDecoratorList"],
                                 "command":self.getjobdesignercommand(extid)["command"],
                                 "numJobs":self.getlistofparameterranges(extid)["numJobs"]
                                 })
        except Exception, e:
            return self.fail("Couldn't load the job file! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def saveas(self, extid, path):
        logging.getLogger("system.extensions.jobsubmssion").debug("save CommandLine to file with virtual path='%s'" % (str(path)))

        try:
            # realpath = vfs.translateVirtualPath(uname, path)

            logging.getLogger("system.extensions.jobsubmssion").debug("Resolved virtual path='%s' to path='%s'" % (str(path), str(realpath)))
            # self.getCommandLineDesigner().saveAs(realpath)
            self.getCommandLineDesigner().saveAs(path)

            return self.success({"success": True})
        except Exception, e:
            return self.fail("Couldn't load the job file! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getparameterrange(self, extid, script):
        try:
            # logging.getLogger("system.batchsystem").info(script)
            parameterRange = vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, "BatchSystemManager.Core.ParameterRange.ParameterRange")

            if (script):
                parameterRange.setScript(script)
            else:
                raise Exception("No python script given.")

            parameterRange.updateValue()
            return self.success({"success": True, "valueslist":str(parameterRange.getValues()), "scriptStatus": parameterRange.getScriptStatus()})
        except Exception, e:
            return self.fail("Couldn't parse the python script! <br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getlistofparameterranges(self, extid):
        try:
            returnValuesList = []
            for parameterRange in self.getCommandLineDesigner().getParameterRangesFlat():
                returnValuesList.append({
                                         "name" : parameterRange["name"] if "name" in parameterRange else "",
                                         "values" : parameterRange["values"] if "values" in parameterRange else "",
                                         "script" : parameterRange["script"] if "script" in parameterRange else "",
                                         "active" : parameterRange["active"] if "active" in parameterRange else "",
                                         "scriptStatus": parameterRange["scriptStatus"] if "scriptStatus" in parameterRange else ""
                                         })
            numJobs = self.getCommandLineDesigner().getNumberOfJobs()
            return self.success({"success": True, "parameterRangeList":returnValuesList, "numJobs":numJobs})
        except Exception, e:
            return self.fail("Couldn't retrieve the list of available parameter ranges! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getlistofoptiondecorators(self, extid):
        try:
            returnValuesList = []
            for optionDecorator in self.getCommandLineDesigner().getOptionDecoratorsFlat():
                returnValuesList.append({
                                         "name" : optionDecorator["name"] if "name" in optionDecorator else "",
#                                         "value" : optionDecorator["value"] if "value" in optionDecorator else "",
                                         "script" : optionDecorator["script"] if "script" in optionDecorator else ""
                                         })

            return self.success({"success": True, "optionDecoratorList":returnValuesList})
        except Exception, e:
            return self.fail("Couldn't retrieve the list of available option decorators! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def addparameterrange(self, extid, name, active, values, script):
        logging.getLogger("system.extensions.jobsubmssion").debug("Adding parameter range with name='%s', active='%s', values='%s', and script='%s'" % (str(name), str(active), str(values), str(script)))
        try:
            self.getCommandLineDesigner().addParameterRange(name, active, values, script)

            """return all parameter ranges to let the user see if the parameter range was successfully added"""
            returnValuesDict = {}

            listofparameterranges = self.getlistofparameterranges(extid)
            returnValuesDict["parameterRangeList"] = listofparameterranges["parameterRangeList"]
            returnValuesDict["numJobs"] = listofparameterranges["numJobs"]

            """ add also a new option decorator """
            name = name + "_SimpleDecorator"
            script = "return valueDict['%s']" % (name)
            returnValuesDict["optionDecoratorList"] = self.addoptiondecorator(extid, name, script)["optionDecoratorList"]

            returnValuesDict["optionList"] = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "numJobs":returnValuesDict["numJobs"], "parameterRangeList":returnValuesDict["parameterRangeList"], "optionDecoratorList":returnValuesDict["optionDecoratorList"], "optionList":returnValuesDict["optionList"]})
        except Exception, e:
            return self.fail("Couldn't add the parameter range! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def modifyparameterrange(self, extid, name, newValues):
        try:
            """needed for conversion of "stringified" list via eval(JSON.stringify(array))"""
            true = True
            false = False
            """convert newValues of type 'JSON.stringify(array))' back to python objects """
            newValues = eval(newValues)

            for change in newValues:
                self.getCommandLineDesigner().modifyParameterRange(name, change["key"], change["value"])

            """return all parameter ranges to let the user see if the parameter range was successfully added"""
            returnValuesDict = {}

            listofparameterranges = self.getlistofparameterranges(extid)
            returnValuesDict["parameterRangeList"] = listofparameterranges["parameterRangeList"]
            returnValuesDict["numJobs"] = listofparameterranges["numJobs"]

            return self.success({"success": True, "numJobs":returnValuesDict["numJobs"], "parameterRangeList":returnValuesDict["parameterRangeList"]})
        except Exception, e:
            return self.fail("Couldn't modify the parameter range! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def removeparameterranges(self, extid, parameterrangeslist):
        try:
            values = []
            """needed for conversion of "stringified" list via eval(JSON.stringify(array))"""
            true = True
            false = False
            """convert parameterrangeslist of type 'JSON.stringify(array))' back to python objects """
            parameterrangeslist = eval(parameterrangeslist)
            self.getCommandLineDesigner().removeParameterRanges(parameterrangeslist)

            """return all parameter ranges to let the user see if the parameter range was successfully added"""
            returnValuesDict = {}

            listofparameterranges = self.getlistofparameterranges(extid)
            returnValuesDict["parameterRangeList"] = listofparameterranges["parameterRangeList"]
            returnValuesDict["numJobs"] = listofparameterranges["numJobs"]

            return self.success({"success": True, "numJobs":returnValuesDict["numJobs"], "parameterRangeList":returnValuesDict["parameterRangeList"]})
        except Exception, e:
            return self.fail("Couldn't remove the parameter ranges! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getlistofoptions(self, extid):
        try:
            returnValuesDict = {}

            for option in self.getCommandLineDesigner().getOptionsFlat():
                group = option["group"] if "group" in option else "default"

                if not group in returnValuesDict:
                    returnValuesDict[group] = []

                returnValuesDict[group].append({
                                         "name" : option["name"] if "name" in option else "",
                                         "optionString" : option["optionString"] if "optionString" in option else "",
                                         "value" : option["value"] if "value" in option else "",
                                         "active" : option["active"] if "active" in option else "",
                                         "group" : group,
                                         "decorator" : option["decorator"] if "decorator" in option else ""
                                         })

            return self.success({"success": True, "optionList":returnValuesDict})
        except Exception, e:
            return self.fail("Couldn't retrieve the list of available options! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def addoption(self, extid, name, optionString, active, value, group, decorator):
        try:
            values = []
            self.getCommandLineDesigner().addOption(None, name, optionString, active, value, group, decorator)

            """return all options to let the user see if the option was successfully added"""
            returnValuesDict = {}
            returnValuesDict["optionList"] = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "optionList":returnValuesDict["optionList"]})
        except Exception, e:
            return self.fail("Couldn't add the option! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def removeoptions(self, extid, optionslist):
        try:
            values = []
            """needed for conversion of "stringified" list via eval(JSON.stringify(array))"""
            true = True
            false = False
            """convert parameterrangeslist of type 'JSON.stringify(array))' back to python objects """
            optionslist = eval(optionslist)
            self.getCommandLineDesigner().removeOptions(optionslist)

            """return all options to let the user see if the option was successfully added"""
            returnValuesDict = {}
            returnValuesDict["optionList"] = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "optionList":returnValuesDict["optionList"]})
        except Exception, e:
            return self.fail("Couldn't add the option! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def modifyoption(self, extid, name, newValues):
        logging.getLogger("system.extensions.jobsubmssion").debug("Modify option with name='%s' and new values '%s'" % (str(name), str(newValues)))

        try:
            """needed for conversion of "stringified" list via eval(JSON.stringify(array))"""
            true = True
            false = False
            """convert newValues of type 'JSON.stringify(array))' back to python objects """
            newValues = eval(newValues)

            for change in newValues:
                self.getCommandLineDesigner().modifyOption(name, change["key"], change["value"])

            """return all options to let the user see if the option was successfully added"""
            returnValuesDict = {}
            returnValuesDict["optionList"] = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "optionList":returnValuesDict["optionList"]})
        except Exception, e:
            return self.fail("Couldn't modify the option! <br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def addoptionlist(self, extid, optionList):
        try:
            """needed for conversion of "stringified" list via eval(JSON.stringify(array))"""
            true = True
            false = False

            """convert optionList of type 'JSON.stringify(array))' back to python objects """
            optionList = eval(optionList)

            for optiongroup in optionList:
                for option in optiongroup:
                    name = option["name"] if "name" in option else "unknown"
                    optionString = option["optionString"] if "optionString" in option else ""
                    active = option["active"] if "active" in option else False
                    value = option["value"] if "value" in option else ""
                    group = option["group"] if "group" in option else "default"
                    decorator = option["decorator"] if "decorator" in option else ""

                    self.getCommandLineDesigner().addOption(None, name, optionString, active, value, group, decorator)

            """return all options to let the user see if the option was successfully added"""
            returnValuesDict = {}
            returnValuesDict["optionList"] = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "optionList":returnValuesDict["optionList"]})
        except Exception, e:
            return self.fai.l("Couldn't add the option! <br />Reason: %s" % str(e))



    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def addoptiondecorator(self, extid, name, script):
        try:
            self.getCommandLineDesigner().addOptionDecorator(None, name, script)

            """return all parameter ranges to let the user see if the parameter range was successfully added"""
            returnValuesList = self.getlistofoptiondecorators(extid)["optionDecoratorList"]

            """update also list of available options, because an option decorator could be removed or deleted"""
            optionList = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "optionDecoratorList":returnValuesList, "optionList":optionList})

        except Exception, e:
            return self.fail("Couldn't add the option decorator! <br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def modifyoptiondecorator(self, extid, name, newValues):
        try:
            """needed for conversion of "stringified" list via eval(JSON.stringify(array))"""
            true = True
            false = False
            """convert newValues of type 'JSON.stringify(array))' back to python objects """
            newValues = eval(newValues)

            for change in newValues:
                self.getCommandLineDesigner().modifyOptionDecorator(name, change["key"], change["value"])

            """return all parameter ranges to let the user see if the parameter range was successfully added"""
            returnValuesList = self.getlistofoptiondecorators(extid)["optionDecoratorList"]

            """update also list of available options, because an option decorator could be removed or deleted"""
            optionList = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "optionDecoratorList":returnValuesList, "optionList":optionList})

        except Exception, e:
            return self.fail("Couldn't modify the option decorator! <br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def removeoptiondecorators(self, extid, decoratorslist):
        try:
            values = []
            """needed for conversion of "stringified" list via eval(JSON.stringify(array))"""
            true = True
            false = False
            """convert decoratorslist of type 'JSON.stringify(array))' back to python objects """
            decoratorslist = eval(decoratorslist)
            self.getCommandLineDesigner().removeOptionDecorators(decoratorslist)

            returnValuesList = self.getlistofoptiondecorators(extid)["optionDecoratorList"]

            """update also list of available options, because an option decorator could be removed or deleted"""
            optionList = self.getlistofoptions(extid)["optionList"]

            return self.success({"success": True, "optionDecoratorList":returnValuesList, "optionList":optionList})
        except Exception, e:
            return self.fail("Couldn't remove the decorators! <br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def setjobdesignercommand(self, extid, command):
        try:
            self.getCommandLineDesigner().setCommand(command)

            return self.success({"success": True, "command":self.getCommandLineDesigner().getCommand()})
        except Exception, e:
            return self.fail("Couldn't set the command  for the JobDesigner!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getjobdesignercommand(self, extid):
        try:
            cmd = self.getCommandLineDesigner().getCommand()
            logging.getLogger("system.extensions.jobsubmssion").debug("Got the following command from the CommandLineDesigner RPC instance: '%s'" % (cmd))

            return self.success({"success": True, "command":cmd})
        except Exception, e:
            return self.fail("Couldn't get the command  for the JobDesigner!<br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getcommandlines(self, extid):
        try:
            commandLines = self.getCommandLineDesigner().buildCommandLines()

            for cmdLine in commandLines:
                logging.getLogger("system.extensions.jobsubmssion").debug("Got the following command lines from the ParameterRange RPC instance: '%s'" % (cmdLine))

            return self.success({"success": True, "commandLines":commandLines})
        except Exception, e:
            return self.fail("Couldn't build the command lines for the JobDesigner!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getstatus(self, extid):
        try:
            logging.getLogger("system.extensions.jobsubmssion").debug("getstatus")

            returnValuesDict = {}

            listofparameterranges = self.getlistofparameterranges(extid)
            returnValuesDict["parameterRangeList"] = listofparameterranges["parameterRangeList"]
            returnValuesDict["numJobs"] = listofparameterranges["numJobs"]
            returnValuesDict["optionDecoratorList"] = self.getlistofoptiondecorators(extid)["optionDecoratorList"]
            returnValuesDict["optionList"] = self.getlistofoptions(extid)["optionList"]
            returnValuesDict["command"] = self.getjobdesignercommand(extid)["command"]

            return self.success({"success": True, "numJobs":returnValuesDict["numJobs"], "parameterRangeList":returnValuesDict["parameterRangeList"], "optionDecoratorList":returnValuesDict["optionDecoratorList"], "optionList":returnValuesDict["optionList"], "command":returnValuesDict["command"]})
        except Exception, e:
            return self.fail("Couldn't get the command  for the JobDesigner!<br />Reason: %s" % str(e))


    """END: Job DESIGNER FORM ajax requests"""

    """START: Job Submission Ajax requests"""

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def runJobs(self, joblist):
        try:
            # submit
            true = True
            false = False
            joblist = eval(joblist)

            for job in joblist:
                command = job["command"] if "command" in job else ""
                manager = job["manager"] if "manager" in job else ""
                preExecutionScriptText = job["preExecutionScriptText"] if "preExecutionScriptText" in job else ""
                postExecutionScriptText = job["postExecutionScriptText"] if "postExecutionScriptText" in job else ""
                outputPath = job["outputPath"] if "outputPath" in job else ""

                logging.getLogger("system.extensions.jobsubmssion").debug("Executing job with command='%s', manager='%s', preExecutionScriptText='%s', postExecutionScriptText='%s', outputPath='%s' " % (command, manager, preExecutionScriptText, postExecutionScriptText, outputPath))
                self.extension._jobPool.submit(command, batchManagerFolder=self._getBatchManagerOutputFolder(), manager=manager, preExecutionScriptText=preExecutionScriptText, postExecutionScriptText=postExecutionScriptText, outputPath=outputPath)

            return self.success()
        except Exception, e:
            vispa.log_exception()
            return self.fail("Couldn't submit the job!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def restartJobs(self, jobids):
        try:
            true = True
            false = False
            jobids = eval(jobids)

            for jobid in jobids:
                self.extension._jobPool.restartJob(jobid)

            return self.success({})
        except Exception, e:
            return self.fail("Couldn't restart job!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def removeJobs(self, jobids):

        try:
            true = True
            false = False
            jobids = eval(jobids)

            for jobid in jobids:
                self.extension._jobPool.removeJob(jobid)

            return self.success({})
        except Exception, e:
            return self.fail("Couldn't remove job!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def stopJobs(self, jobids):
        try:
            true = True
            false = False
            jobids = eval(jobids)

            for jobid in jobids:
                self.extension._jobPool.stopJob(jobid)

            return self.success({})
        except Exception, e:
            return self.fail("Couldn't stop job!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getJobDetails(self, jobid):
        try:
            stdout = self.extension._jobPool.getJobOutput(jobid)
            stderr = self.extension._jobPool.getJobError(jobid)

            return self.success({"data":{"stdout": stdout, "stderr":stderr}})
        except Exception, e:
            return self.fail("Couldn't get job details!<br />Reason: %s" % str(e))


    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getJobCommand(self, jobid):
        try:
            command = self.extension._jobPool.getJobCommand(jobid)

            return self.success({"data": command})
        except Exception, e:
            return self.fail("Couldn't get job command!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def getJobData(self):
        try:
            data = self.extension._jobPool.getJobData(self._getBatchManagerOutputFolder())

            return self.success({"data": data})
        except Exception, e:
            vispa.log_exception()
            return self.fail("Couldn't get job data!<br />Reason: %s" % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def isBatchManagerAvailable(self):
        try:
            return self.success({"data": True})
        except Exception, e:
            return self.fail("Couldn't get BatchManager availability!<br />Reason: %s" % str(e))

    """END: Job Submission Ajax requests"""

    def _getBatchManagerOutputFolder(self):
#        uname = self.get("uname") if uname is None else uname
#        if uname not in self.__batchManagerOutputFolder_vfs:
#            vfs = self._get_filesystem_instance(uname)
#            self.__batchManagerOutputFolder_vfs[uname] = vfs.translateVirtualPath(uname, self.__batchManagerOutputFolder)

        return self.__batchManagerOutputFolder

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.workspace()
    # cherrypy.tools.render(template="JobDashboard.html", extension_name="jobmanagement")
    def loadjobdashboardview(self, extid):
        # FIXME#available_bm_html = self.getAvailableBatchManager()
        # FIXME#contentDict = {"extid": extid, "availableBatchManager":available_bm_html}

        contentDict = {"extid": extid}

        template = cherrypy.engine.publish("lookup_template", "JobDashboard.html", "", "jobmanagement").pop()
        return template.render(**contentDict)
        # return contentDict

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.workspace()
    def loadjobdesignerview(self, extid):
        contentDict = {"extid": extid}

        template = cherrypy.engine.publish("lookup_template", "JobDesigner.html", "", "jobmanagement").pop()
        return template.render(**contentDict)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.workspace()
    def loadjobsubmissionview(self, extid):
        contentDict = {"extid": extid}

        template = cherrypy.engine.publish("lookup_template", "JobSubmission.html", "", "jobmanagement").pop()
        return template.render(**contentDict)