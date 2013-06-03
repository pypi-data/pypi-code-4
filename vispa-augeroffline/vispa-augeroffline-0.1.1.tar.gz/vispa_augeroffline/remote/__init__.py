from lxml import etree as ET
import copy
import ast
import logging
import os
import sys
import uuid
import shutil
import re
import subprocess
import hashlib
import numpy as np
import pickle
from collections import OrderedDict
from StringIO import StringIO
import tempfile


class AugerOfflineRpc:
    def exposed_dummy(self):
        return ",".join(sys.path)
    
    def __get_keys_to_value(self, dictionary, module_branch_name):
        keys = []
        for key, value in dictionary.iteritems():
            if(value == module_branch_name):
                keys.append(str(key))
        return keys

        
    
    def __md5Checksum(self, filePath):
        fh = open(filePath, 'rb')
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

    #===========================================================================
    # checks whether a file has changed or not
    # returns true if file has changed 
    #===========================================================================
    def __get_file_status(self, source, destination):
        if(not os.path.exists(destination)):
            return True
        md5_old = self.__md5Checksum(destination)
        md5_new = self.__md5Checksum(source)
        if(md5_old != md5_new):
            self.__log(source +" has changed.")
            return True
        else:
            return False


    def __log(self, message):
        f = open(self.__log_filename, "a")
        f.write(message + "\n")
        f.close()



    def __init__(self, db_default_config):
        handle, self.__log_filename = tempfile.mkstemp(prefix="augeroffline-log-")
        os.close(handle)
        self.__log("__init__")
        self.__db_default_config = db_default_config

        __home = os.getenv("HOME")
        self.__workspace_dir = os.path.join(__home, ".vispa", "extensions", "augeroffline")
        if(not os.path.exists(self.__workspace_dir)):
            self.__log("mkdir "+ str(self.__workspace_dir))
            os.makedirs(self.__workspace_dir)
        
        self.__log("os.path.dirname(__file__): " +os.path.dirname(os.path.abspath(os.sep.join(__path__))))
        if(self.__get_file_status(os.path.join(os.path.dirname(os.path.abspath(__file__)), "executeOffline.py"), os.path.join(self.__workspace_dir, "executeOffline.py"))):    
            shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "executeOffline.py"), os.path.join(self.__workspace_dir, "executeOffline.py"))
        else:
            self.__log("executeOffline.py does not have changed")
        
        
        # get uuid
        self.__uuid = uuid.uuid4()

        self.__AUGEROFFLINEROOT = os.getenv('AUGEROFFLINEROOT')
        if(self.__AUGEROFFLINEROOT == None):
            self.__log("environment variable AUGEROFFLINEROOT not set")
            raise Exception("environment variable AUGEROFFLINEROOT not set")

        self.__configPath = os.path.join(self.__AUGEROFFLINEROOT, "share/auger-offline/config")
        
        #=======================================================================
        # get list of available modules
        #=======================================================================
#        subprocess.check_output(os.path.join(self.__AUGEROFFLINEROOT,"bin","AugerOffline"))
        cmd = [os.path.join(self.__AUGEROFFLINEROOT,"bin","AugerOffline"),"--show-available-modules"]
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.communicate()[0]
        self.__available_modules = np.loadtxt(StringIO(output), dtype=str)
        self.__log("available modules: \n"+str(self.__available_modules))
#        
        self.__modules = {}
        self.__dict_module_id_to_classname = {}


        #### load bootstrap
        self.__parser = ET.XMLParser(remove_blank_text = True, remove_comments = True, attribute_defaults = False, recover = True, resolve_entities = True)

        self.__BootstrapRoot = ET.fromstring("<bootstrap xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\""+os.path.join(self.__configPath,"bootstrap.xsd")+"\" xmlns:xlink=\"http://www.auger.org/schema/types\"><centralConfig /><parameterOverrides /></bootstrap>")
    

        ''' generate module sequence xml '''
        self.__ModuleSequenceRoot = ET.fromstring("<sequenceFile xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:noNamespaceSchemaLocation='" + os.path.join(self.__configPath, "ModuleSequence.xsd") + "'><enableTiming/><moduleControl></moduleControl></sequenceFile>")


        #------------------------------------------------ restore programm state
        if(os.path.exists(os.path.join(self.__workspace_dir,"__detector_config.p"))):
            self.__detector_config = pickle.load( open(os.path.join(self.__workspace_dir,"__detector_config.p"), "rb"))
        if(os.path.exists(os.path.join(self.__workspace_dir,"__module_config.p"))):
            self.__module_config = pickle.load(open(os.path.join(self.__workspace_dir,"__module_config.p"), "rb"))
        if(os.path.exists(os.path.join(self.__workspace_dir,"__modules.p"))):
            self.__modules = pickle.load(open(os.path.join(self.__workspace_dir,"__modules.p"), "rb"))
        if(os.path.exists(os.path.join(self.__workspace_dir,"__dict_module_id_to_classname.p"))):
            self.__dict_module_id_to_classname = pickle.load(open(os.path.join(self.__workspace_dir,"__dict_module_id_to_classname.p"), "rb"))
        if(os.path.exists(os.path.join(self.__workspace_dir,"__BootstrapRoot.xml"))):
            with open(os.path.join(self.__workspace_dir,"__BootstrapRoot.xml"),'rb') as f:
                self.__BootstrapRoot=ET.parse(f).getroot()


    #===========================================================================
    # the initialize function saves the moduleConfig and the detectorConfig files from the DB into a dicionary structure on remote site
    #===========================================================================
    ''' error codes: 
      001: one or more files can't be read in
      010: all files can't be read in
    '''
    def initialize(self, moduleConfig, detectorConfig):
        self.__log("initialize")
        
        #----------------------------------------------- reset old program state
        self.__module_config = {}
        self.__modules = {}
        self.__dict_module_id_to_classname = {}
        self.__detector_config = {}
        self.__BootstrapRoot = ET.fromstring("<bootstrap xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\""+os.path.join(self.__configPath,"bootstrap.xsd")+"\" xmlns:xlink=\"http://www.auger.org/schema/types\"><centralConfig /><parameterOverrides /></bootstrap>")
        
        XLINK_NAMESPACE = "http://www.auger.org/schema/types"
        XLINK = "{%s}" % XLINK_NAMESPACE
        NSMAP = {"xlink": XLINK_NAMESPACE}
        
        moduleConfig = ast.literal_eval(moduleConfig)
        self.__module_config = moduleConfig
#        self.__log("module_config = "+str(moduleConfig))
        result = 0
        # store all modules that should be available in VISPA-Offline in a dict data structure
        keys_to_remove = []
        for category, module_config_filename in moduleConfig.iteritems():
            module_config_path = os.path.join(self.__configPath, module_config_filename)
            # check if path actually points to a file
            if(not os.path.isfile(module_config_path)):
                result = result | 1
                keys_to_remove.append(category)
                self.__log("could not find "+str(module_config_path))
                continue
            self.__module_config.update({category:os.path.join(self.__configPath,module_config_filename)})

            #------------------------------------------- read in default modules from xml
            module_config_string = open(module_config_path, "rb").read()
            module_config_string = "<bootstrap xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xlink=\"http://www.auger.org/schema/types\">" + module_config_string + "</bootstrap>"
            module_config_tree = ET.parse(StringIO(module_config_string), self.__parser)
            module_config_root = module_config_tree.getroot().find("./defaultConfig")
            
            
            for item in module_config_root:
                module_branch_name = item.attrib.get('id')
                module_path = item.attrib[XLINK+"href"]
#                self.__log("searching module indentifier for branch name: "+module_branch_name)
                if(module_branch_name in self.__available_modules):
                    self.__dict_module_id_to_classname.update({module_branch_name:module_branch_name})
#                    self.__log("found "+module_branch_name+":"+module_branch_name)
                else:
                    for module_identifier in self.__available_modules:
                        for i in range(1,4):
                            if(module_identifier[:-i] == module_branch_name):
                                self.__dict_module_id_to_classname.update({module_identifier:module_branch_name})
#                                self.__log("\tfound "+module_identifier+":"+module_branch_name)
                                break
                    
                module_identifiers = self.__get_keys_to_value(self.__dict_module_id_to_classname, module_branch_name)
                for module_identifier in module_identifiers:
                    if (self.__modules.has_key(module_identifier)):
                        categories = self.__modules[module_identifier]["category"]
                        if not category in categories:
                            categories.append(category)
                    else:
                        categories = ["All Modules"]
                        categories.append(category)
                    
                    self.__modules.update({str(module_identifier): {"module_name": module_branch_name, "category": categories, "path_to_xmlconfig": module_path}})
        
        # remove non existing config links
        for key in keys_to_remove:
            moduleConfig.pop(key, None)
            
        if(len(moduleConfig) == 0):
            result = 2
            
        keys_to_remove = []
        self.__detector_config = ast.literal_eval(detectorConfig)
        # store all detector config objects that should be available in VISPA-Offline in a dict data structure
        for key, module_config_filename in self.__detector_config.iteritems():
            module_config_path = os.path.join(self.__configPath, module_config_filename)
            # check if path actually points to a file, otherwise remove it from list of filenames
            if(not os.path.isfile(module_config_path)):
                result = result | 1
                keys_to_remove.append(category)
                self.__log("could not find "+str(module_config_path))
                continue
            self.__detector_config.update({key:os.path.join(self.__configPath,module_config_filename)})
            
        # remove non existing config links
        for key in keys_to_remove:
            detectorConfig.pop(key, None)
            
        if(len(self.__detector_config) == 0):
            result = 2

        #---------------------------------------------------- save program state
        pickle.dump(self.__detector_config, open(os.path.join(self.__workspace_dir,"__detector_config.p"), "wb"))
        pickle.dump(self.__module_config, open(os.path.join(self.__workspace_dir,"__module_config.p"), "wb"))
        pickle.dump(self.__modules, open(os.path.join(self.__workspace_dir,"__modules.p"), "wb"))
        pickle.dump(self.__dict_module_id_to_classname, open(os.path.join(self.__workspace_dir,"__dict_module_id_to_classname.p"), "wb"))
        

        return result

    def resetAllModuleOptions(self):
        bootstrapOverride = self.__BootstrapRoot.find("parameterOverrides")
        if(bootstrapOverride is not None):
            bootstrapOverride.clear()
        return 0


    def get_auger_offline_path(self):
        return self.__workspace_dir

    # deprecated 
    def getListOfModules(self, category):

        self.__log("remote getListOfModules for category " +str(category))
        listOfModules = []
        for module_identifier, value in self.__modules.iteritems():
            if(category in value["category"]):
                listOfModules.append(module_identifier)
                
        if(len(listOfModules) == 0):
            self.__log("module config does not have category " + category)
            return -1

#        self.__log(str(listOfModules.sort()))
        listOfModules.sort()
        return listOfModules
    
    def get_available_modules(self):

        self.__log("remote get_available_modules()")
        
        listOfModulesPerCategory = {}
        for module_identifier, value in sorted(self.__modules.iteritems()):
            for category in value["category"]:
                tmp_modules = []
                if(listOfModulesPerCategory.has_key(category)):
                    tmp_modules = listOfModulesPerCategory[category]
                tmp_modules.append({'module-identifier': module_identifier, 'class':'offline-module'})
                listOfModulesPerCategory.update({category: tmp_modules})
#        self.__log(str(listOfModulesPerCategory))
        
        listOfModules = []
        for category, module_list in listOfModulesPerCategory.iteritems():
            listOfModules.append({'category-name':category, 'module-list': module_list})
            
        self.__log(str(listOfModules))
        listOfModules.sort()
        
        # add steering symbols
#        listOfModules.insert(0,{'category-name':'steering symbols', 'module-list': [{'module-identifier': 'loop', 'class':'steering-symbol'}, {'module-identifier': 'try', 'class':'steering-symbol'}]})

        return listOfModules


    def getModuleOptions(self, module_identifier):
#        self.__log("get module options for " +str(module_identifier))
        # the options will be stored in a dict with key = optionname of dicts (containing optionvalue, default value, unit etc)
        dictOfOptions = {};
        
        if not self.__modules.has_key(module_identifier):
            self.__log("no key found for module "+ module_identifier)
            return -1
        modulePath = self.__modules[module_identifier]["path_to_xmlconfig"]
        moduleName = self.__modules[module_identifier]["module_name"]
#        dictOfOptions['module-name'] = moduleName
#        dictOfOptions['module-options'] = []
        
        if(not os.path.exists(modulePath)):
            self.__log("no xml configuration file for module " + str(module_identifier) + " at " + str(modulePath))
            return -1
        
        moduleOptionsTree = ET.parse(modulePath, self.__parser)
        moduleOptionsRoot = moduleOptionsTree.getroot()
        
        self.__log(ET.tostring(moduleOptionsRoot, pretty_print=True))
        for option in moduleOptionsRoot:
            dict_of_option = {}
            # ----------------------------- check if option has additional children
            if(len(list(option)) > 0):
                self.__log("option "+option.tag+ " has " +str(len(list(option))) +" children")
                for child in option:
                    dict_of_option_2 = {}
                    dict_of_option_2.update({"value":str(child.text).strip()})
                    dict_of_option_2.update({"default_value":str(child.text).strip()})
                    if(child.get('unit') is not None):
                        dict_of_option_2.update({"unit":str(child.get('unit')).strip()})
                        dict_of_option_2.update({"default_unit":str(child.get('unit')).strip()})
                    dict_of_option.update({child.tag:dict_of_option_2})
            else:
                dict_of_option.update({"value":str(option.text).strip()})
                dict_of_option.update({"default_value":str(option.text).strip()})
                if(option.get('unit') is not None):
                    dict_of_option.update({"unit":str(option.get('unit')).strip()})
                    dict_of_option.update({"default_unit":str(option.get('unit')).strip()})
            dictOfOptions.update({option.tag: dict_of_option})
            
        
        
        ''' check weather the option was overridden in the bootstrap file '''
        bootstrapOverride = self.__BootstrapRoot.find("parameterOverrides")
        node = bootstrapOverride.find(".//" + moduleName)
        if(node is not None):
            for option in list(node):
                dict_of_option = dictOfOptions[option.tag]
                # ----------------------------- check if option has additional children
                if(len(list(option)) > 0):
#                    self.__log("option "+option.tag+ " has " +str(len(list(option))) +" children")
                    for child in option:
                        dict_of_option_2 = {}
                        # check if value is empty string
                        if(child.text is None):
                            dict_of_option_2.update({"value":""})
                        else:
                            dict_of_option_2.update({"value":str(child.text).strip()})
                        if(child.get('unit') is not None):
                            dict_of_option_2.update({"unit":str(child.get('unit')).strip()})
                        dict_of_option.update({child.tag:dict_of_option_2})
                else:
                    # check if value is empty string
                    if(option.text is None):
                        dict_of_option.update({"value":""})
                    else:
                        dict_of_option.update({"value":str(option.text).strip()})
                    if(option.get('unit') is not None):
                        dict_of_option.update({"unit":str(option.get('unit')).strip()})
                dictOfOptions.update({option.tag: dict_of_option})
        
            
            
        self.__log("dictOfOptions: "+str(dictOfOptions))
        if(len(dictOfOptions) == 0):
#            self.__log("module " + str(module_identifier) + " has no options specified in xml file ")
            return -1
             
        return str(dictOfOptions)
        

    def setModuleOptions(self, module_identifier, moduleOptions):
        moduleName = self.__dict_module_id_to_classname[module_identifier]
        self.__log("setModuleOptions for module "+ module_identifier+ ":")
        self.__log(str(moduleOptions))
        
        bootstrapOverride = self.__BootstrapRoot.find("parameterOverrides")
        node = bootstrapOverride.find(".//" + moduleName)
        if(node is None):
            a = ET.SubElement(bootstrapOverride, "configLink", {"id":moduleName})
            node = ET.SubElement(a, moduleName)
        
        for option_name, value, unit, parent in moduleOptions:
            self.__log(str(option_name) +","+str(value)+","+str(unit)+","+str(parent))
            if(parent):
                c = node.find("./" + str(parent))
                if(c is None):
                    c = ET.SubElement(node, str(parent))
                child = c.find("./"+str(option_name))
                if(child is None):
                    child = ET.SubElement(c,str(option_name))
                child.text = str(value)
                if(unit is not None):
                    child.set("unit", str(unit))
            else:
                c = node.find("./" + str(option_name))
                if(c is None):
                    c = ET.SubElement(node, str(option_name))
                c.text = str(value)
                if(unit is not None):
                    c.set("unit", str(unit))
                    
        #---------------------------------------------------- save program state
        with open(os.path.join(self.__workspace_dir,"__BootstrapRoot.xml"),'wb') as f:
            f.write(ET.tostring(self.__BootstrapRoot))
        
        
        return 0





    def loadModuleOptions(self, pathToBootstrap):
        tree = ET.parse(pathToBootstrap, self.__parser)
        self.__BootstrapRoot = tree.getroot()
        self.__log("self.__BootstrapRoot:\n"+ET.tostring(self.__BootstrapRoot, pretty_print=True))
        self.__log("removing defaultConfig")
        for element in self.__BootstrapRoot.findall(".//defaultConfig"):
            self.__log("removing element "+ ET.tostring(element))
            element.getparent().remove(element)
        
        
        stringIO = ET.tostring(self.__BootstrapRoot, pretty_print=True)
        self.__BootstrapRoot = ET.fromstring(stringIO,self.__parser)
        self.__log(ET.tostring(self.__BootstrapRoot, pretty_print=True))
        
        #---------------------------------------------------- save program state
        with open(os.path.join(self.__workspace_dir,"__BootstrapRoot.xml"),'wb') as f:
            f.write(ET.tostring(self.__BootstrapRoot))

    def openModuleSequenceXML(self, path):
        tree = ET.parse(path, self.__parser)
        self.__ModuleSequenceRoot = tree.getroot()
        
        

        pass

    def openBootstrapXML(self, path):
        self.loadModuleOptions(path)
        
        XLINK_NAMESPACE = "http://www.auger.org/schema/types"
        XLINK = "{%s}" % XLINK_NAMESPACE
        NSMAP = {"xlink": XLINK_NAMESPACE}
        
        config_link_modulesequence = self.__BootstrapRoot.find(".//configLink[@id='ModuleSequence']")
        module_sequence_filename = os.path.basename(config_link_modulesequence.attrib[XLINK+"href"])
        module_sequence_path = os.path.join(os.path.dirname(path),config_link_modulesequence.attrib[XLINK+"href"])
        self.openModuleSequenceXML(module_sequence_path)
        
        #-------------------------------------------------- open eventfilereader
        config_link_eventfilereader = self.__BootstrapRoot.find(".//configLink[@id='EventFileReader']")
        event_file_reader_filename = os.path.basename(config_link_eventfilereader.attrib[XLINK+"href"])
        tree = ET.parse(os.path.join(os.path.dirname(path),config_link_eventfilereader.attrib[XLINK+"href"]), self.__parser)
        event_file_reader_root = tree.getroot()
        input_file_type = event_file_reader_root.find("./InputFileType").text.strip().replace(" ","")
        input_file_names = event_file_reader_root.find("./InputFilenames").text.strip().replace(" ","")
        
        return {"moduleSequence": self.returnModuleSequence(), "moduleSequenceFilename": module_sequence_filename, "input_file_type":input_file_type,"input_file_names":input_file_names, "event_file_reader_filename": event_file_reader_filename}




    def __addItemsToModuleList(self, moduleSequenceList, node, father):
        for item in list(node):
            if(item.tag == "module"):
                moduleSequenceList.append([str(item.text).strip(), ""])
            elif(item.tag == "loop"):
                moduleSequenceList.append([item.tag, item.get("numTimes")])
                self.__addItemsToModuleList(moduleSequenceList, item, node)
            else:
                moduleSequenceList.append([item.tag, ""])
                self.__addItemsToModuleList(moduleSequenceList, item, node)
        if(node.tag == "loop"):
            moduleSequenceList.append(["loop stop", ""])
        elif(node.tag == "try"):
            moduleSequenceList.append(["try stop", ""])
        return 0

    def returnModuleSequence(self):
        self.__log("returnModuleSequence()")
        moduleControl = self.__ModuleSequenceRoot.find("./moduleControl")
        moduleSequence = []
        
        self.__addItemsToModuleList(moduleSequence, moduleControl, self.__ModuleSequenceRoot)
        
        #      self.__log(str(moduleSequence))
        
        return moduleSequence




    def setModuleSequence(self, moduleSequence):
        a = self.__ModuleSequenceRoot.find("./moduleControl")
        a.clear()
        
        parentDict = []
        depth = 0
        currentElement = a
        for module, extraInfo in moduleSequence:
            if(module == "loop"):
                parentDict.append(currentElement)
                depth += 1
                currentElement = ET.SubElement(currentElement, "loop", {"numTimes":str(extraInfo)})
            elif(module == "loop stop"):
                depth -= 1
                currentElement = parentDict[depth]
                pass
            elif(module == "try"):
                parentDict.append(currentElement)
                depth += 1
                currentElement = ET.SubElement(currentElement, "try")
            elif(module == "try stop"):
                depth -= 1
                currentElement = parentDict[depth]
                pass
            else:
                b = ET.SubElement(currentElement, "module")
                b.text = module.strip()




    def saveModuleSequence(self,filepath):
        fModuleSequence = open(filepath, "w")
        fModuleSequence.write(ET.tostring(self.__ModuleSequenceRoot, pretty_print = True))
        fModuleSequence.close()
        
    def saveEventFileReader(self, filepath, input_files, input_file_type):
        eventFileReaderRoot = ET.fromstring('<?xml version="1.0" encoding="iso-8859-1"?><EventFileReader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="'+os.path.join(self.__configPath,'EventFileReader.xsd')+'"><InputFileType></InputFileType><InputFilenames></InputFilenames></EventFileReader>')
        EventFileReaderTree = eventFileReaderRoot.getroottree()
        
        eventFileReaderRoot.find("./InputFileType").text = input_file_type
        filenames_tag = eventFileReaderRoot.find("./InputFilenames")
        for filename in input_files:
            if(filenames_tag.text is None):
                filenames_tag.text = "\n\t"+ filename +"\n"
            else:
                filenames_tag.text = filenames_tag.text + "\t"+ filename +"\n"
        
        docinfo = EventFileReaderTree.docinfo
        fEventFileReader = open(filepath,"w")
        fEventFileReader.write(ET.tostring(EventFileReaderTree,pretty_print=True, xml_declaration=True, encoding=docinfo.encoding))
        fEventFileReader.close()
        
    def saveBootstrap(self, output_folder, filename_bootstrap, filename_modulesequence, filename_eventfilereader):
        # check if output_folder exists
        if (not (os.path.exists(os.path.dirname(output_folder)))):
            return 1
        if(not (os.path.dirname(filename_bootstrap) == '')  and not os.path.exists(os.path.dirname(filename_bootstrap))):
            return 1
        if(not (os.path.dirname(filename_modulesequence) == '')  and not os.path.exists(os.path.dirname(filename_modulesequence))):
            return 1
        if(not (os.path.dirname(filename_eventfilereader) == '')  and not os.path.exists(os.path.dirname(filename_eventfilereader))):
            return 1
        
        XLINK_NAMESPACE = "http://www.auger.org/schema/types"
        XLINK = "{%s}" % XLINK_NAMESPACE
        NSMAP = {"xlink": XLINK_NAMESPACE}
        
        # create modulesequence link
        config_link_modulesequence = self.__BootstrapRoot.find(".//configLink[@id='ModuleSequence']")
        if(config_link_modulesequence is None):
            config_link_modulesequence = ET.SubElement(self.__BootstrapRoot.find("./centralConfig"),"configLink")
            config_link_modulesequence.set("id", "ModuleSequence")
            config_link_modulesequence.set("type", "XML")
        config_link_modulesequence.set(XLINK + "href", filename_modulesequence)
        
        # create eventfilereader link
        config_link_bootstrap = self.__BootstrapRoot.find(".//configLink[@id='EventFileReader']")
        if(config_link_bootstrap is None):
            config_link_bootstrap = ET.SubElement(self.__BootstrapRoot.find("./centralConfig"),"configLink")
            config_link_bootstrap.set("id", "EventFileReader")
            config_link_bootstrap.set("type", "XML")
        config_link_bootstrap.set(XLINK + "href", filename_eventfilereader)
        
        
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!DOCTYPE bootstrap [\n"
        for key, path in self.__detector_config.iteritems():
            xml += "<!ENTITY " + key.replace(" ", "") + " SYSTEM \'" + path + "\'>\n"
        for key,path in self.__module_config.iteritems():
            xml += "<!ENTITY " + key.replace(" ", "") + " SYSTEM \'" + path + "\'>\n"
        xml +="]>\n <bootstrap xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\""+os.path.join(self.__configPath,"bootstrap.xsd")+"\" xmlns:xlink=\"http://www.auger.org/schema/types\" />"   
#        self.__log("xml: \n"+xml)
        xml = ET.parse(StringIO(xml))
        root = xml.getroot()
        root[:] = self.__BootstrapRoot
#        root.text, root.tail = self.__BootstrapRoot.text, self.__BootstrapRoot.tail
        tree = xml
        self.__BootstrapRoot = tree.getroot() 
#        self.__log("Bootstraptree:\n"+ET.tostring(tree))
        
        docinfo = tree.docinfo
#        self.__log(docinfo.encoding)
#        self.__log(ET.tostring(tree, xml_declaration = True, encoding = docinfo.encoding))
        config_link_string = ""
        for key in self.__detector_config.iterkeys():
            config_link_string += "&" + key.replace(" ", "") + ";\n"
        for key in self.__module_config.iterkeys():
            config_link_string += "&" + key.replace(" ", "") + ";\n"
            
        bootstrap_string = ET.tostring(tree, pretty_print=True, xml_declaration = True, encoding = docinfo.encoding)
#        self.__log("bootstrap_string: "+bootstrap_string)
        position  = bootstrap_string.find("<centralConfig>")
        bootstrap_string = bootstrap_string[:position] + config_link_string + bootstrap_string[position:]
        
        fBootstrap = open(filename_bootstrap, "w")
        fBootstrap.write(bootstrap_string)
        fBootstrap.close()
        
        self.__log("return 0")
        return 0

    def setAllInfoLevelTo(self, infoLevelValue):
        for module in ET.iterwalk(self.__ModuleSequenceRoot.find("./moduleControl")):
            if(module[1].tag == "module"):
                moduleName = module[1].text
                listOfOptions = self.getModuleOptions(moduleName)
        
            infoLevel = ""
            if(type(listOfOptions) is int):
                self.__log("module " + moduleName + " has no options")
                continue
            self.__log("listOfOptions: "+ str(listOfOptions))
            self.__log("type of listOfOptions is "+ str(type(listOfOptions)))
            listOfOptions = ast.literal_eval(str(listOfOptions))
            for option,value in listOfOptions.iteritems():
                if(option == "infolevel"):
                    infoLevel = option
                    break
                elif(option == "infoLevel"):
                    infoLevel = option
                    break
                elif(option[0] == "InfoLevel"):
                    infoLevel = option
                    break
                elif(option == "InfoLevel"):
                    infoLevel = option
                    break
            if(infoLevel == ""):
                self.__log("module " + moduleName + " has no option named infolevel")
                continue
            self.__log("setting " + infoLevel + " of module " + moduleName + " to " + str(infoLevelValue))
            self.setModuleOptions(moduleName, [[infoLevel, infoLevelValue, "",""]])










