'''
Created on Sep 23, 2010

@author: Nicklas Boerjesson
@note: The DB upgrader module uses the dal to upgrade a database to a specific step.
@note: It requires a __step_log and a __step_log_application table to handle multiple structures. 
@note: In _step_log_application, DBUpgrader has always the ApplicationGUID = {5113f800-c87b-11df-afd4-0002a5d5c51b}.
'''
import os
from qal.sql.sql_xml import xml_get_text, SQL_XML, find_child_node
from qal.tools.meta_queries import Meta_Queries
from xml.dom.minidom import parse
from qal.sql.sql import Verb_CREATE_TABLE

DBUpgrader_GUID = "{5113f800-c87b-11df-afd4-0002a5d5c51b}"
DBUpgrader_Script_Dir_abs = os.path.dirname(os.path.abspath(os.path.realpath(__file__ ))) 
DBUpgrader_XML_Dir_abs = DBUpgrader_Script_Dir_abs + '/xml'
DBUpgrader_XML_File_abs = DBUpgrader_Script_Dir_abs + '/xml/db_upgrader.xml'
DBUpgraderXML_MinVersion = 0
DBUpgraderXML_MaxVersion = 1


class DBUpgrader(object):
    '''
    classdocs
    '''
    
    dal = None
    debuglevel = 2
    
    def _debug_print(self, _value, _debuglevel = 3):
        if self.debuglevel >= _debuglevel:
            print(_value)

    def __init__(self, _dal):
        '''
        Constructor
        '''
        self.dal = _dal
        self.debuglevel = 2
        
    def get_xml_meta_info(self, _XML_File):
        """Parse all meta info from XML file"""
        
        # Remove all namespace references 
        # TODO: Check if this is all that smart. 
        #_XML = _XML.replace('<' + self.PrefixSQL + ':', '<')
        #_XML = _XML.replace('</' + self.PrefixSQL + ':', '</')
        _Doc = parse(_XML_File)

        _UpgradeNode            = _Doc.childNodes[0]      
        _UpgraderStepNode    = _UpgradeNode.getElementsByTagName("upgrader_version")[0] 
        _UpgraderStep        = int(xml_get_text(_UpgraderStepNode))
        
        if not(_UpgraderStep >= DBUpgraderXML_MinVersion and _UpgraderStep <= DBUpgraderXML_MaxVersion):
            raise Exception("The upgrade XML-file step is unsupported. \
            Supported UpgraderStep range:" + str(DBUpgraderXML_MaxVersion) + " to " + str(DBUpgraderXML_MaxVersion))
        
        _ApplicationGUIDNode = _UpgradeNode.getElementsByTagName("application_guid")[0] 
        _ApplicationGUID     = xml_get_text(_ApplicationGUIDNode) 
        _ApplicationNameNode = _UpgradeNode.getElementsByTagName("application_name")[0] 
        _ApplicationName     = xml_get_text(_ApplicationNameNode)
        _ApplicationDescriptionNode = _UpgradeNode.getElementsByTagName("application_description")[0] 
        _ApplicationDescription = xml_get_text(_ApplicationDescriptionNode)
         
        _StepsNode   = _UpgradeNode.getElementsByTagName("steps")[0] 
        # Make list of steps
        _Steps       = _StepsNode.getElementsByTagName("step")
        # Find the last step in file
        _LastStep    = _Steps[_Steps.length -1]
        _LastStep = int(xml_get_text(_LastStep.getElementsByTagName("step_id")[0]))
                 
        return _UpgraderStep, _ApplicationGUID, _ApplicationName, _ApplicationDescription, _Steps, _LastStep, _LastStep
           
    def check_upgrader_version(self, _Step):    
        """Find out if the version of the upgrader matches that of the file"""
        if int(_Step) > DBUpgraderXML_MaxVersion:
            raise Exception("DBUpgrader.check_upgrader_version: The upgrade file is of a newer format(" + _Step +") than is supported by the upgrader(" + DBUpgraderXML_MaxVersion + " is the newest)!\nPlease upgrade the upgrader software to use this file.")
        if int(_Step) < DBUpgraderXML_MinVersion:        
            raise Exception("DBUpgrader.check_upgrader_version:: The upgrade file is of a older format(" + _Step +") than is supported by the upgrader(" + DBUpgraderXML_MinVersion + " is the oldest)!\nYou need to use older software to upgrade using this file.")

    def read_last_step_log_entry(self, _ApplicationGUID):
        """Return the last step"""
        _GetStep = SQL_XML().xml_file_to_sql(os.path.normpath(DBUpgrader_XML_Dir_abs + '/get_step.xml'),ApplicationGUID = _ApplicationGUID)
        rows = self.dal.query(_GetStep.as_sql(self.dal.db_type))
        if len(rows) > 0:
            return rows[0][0]
        else:
            return 0

    def write_step_log_entry(self,_StepLogID , _StepLogGUID, _StepDescription, _ApplicationGUID):
        """Write a log entry for the upgrade step"""

        _insert = SQL_XML().xml_file_to_sql(os.path.normpath(DBUpgrader_XML_Dir_abs + '/insert_step.xml'), 
                                  StepLogID = _StepLogID, StepLogGUID = _StepLogGUID, 
                                  Description = _StepDescription, ApplicationGUID = _ApplicationGUID)

        tmpSQL = _insert.as_sql(self.dal.db_type)
           
        try:
            self.dal.execute(tmpSQL)
        except Exception as e:
            raise Exception("DBUpgrader.write_step_log_entry: Exception executing SQL:\n" + str(e) + "\nRunning:\n" + tmpSQL)
           
    def get_step_nodes(self, _stepNode):
        """Get a list of step nodes"""
        return find_child_node(_stepNode, 'step_id'),\
        find_child_node(_stepNode, 'step_guid'),\
        find_child_node(_stepNode, 'step_description'),\
        find_child_node(_stepNode, 'statements')
        

    def commit_step(self, _Statements):
        """Commit a step"""
        
        Meta_XML = SQL_XML()
        Meta_XML.debuglevel = self.debuglevel
        # Loop verbs.
        for _CurrStatement in _Statements.childNodes:
            if _CurrStatement.nodeType != _CurrStatement.TEXT_NODE:
                try:
                    _structure = Meta_XML.xml_to_sql_structure(_node = _CurrStatement)
                except Exception as e:
                    raise Exception("DBUpgrader.commit_step: Exception parsing XML statement:\n" + str(e) + "\nNodeName:\n" + find_child_node(_CurrStatement.parentNode,'StepID').nodeName)

                tmpSQL = _structure.as_sql(self.dal.db_type) 
                try:
                    self._debug_print("Executing:\n" + tmpSQL)
                    self.dal.execute(_structure.as_sql(self.dal.db_type))
                    self.dal.commit()                        
                except Exception as e:
                    raise Exception("DBUpgrader.commit_step: Exception executing statement:\n" + str(e) + "\nSQL:\n" + tmpSQL)
                
                
                
                # Handle extra sql statement for table creation. Sometimes needed in some databases.
                if isinstance(_structure,Verb_CREATE_TABLE):
                    for _curr_statements in _structure.get_post_statements():
                        for _curr_SQL in _curr_statements:
                            self._debug_print("Running post statement:\n" + _curr_SQL)
                            try:  
                                self.dal.execute(_curr_SQL)
                                self.dal.commit()                        
                            except Exception as e:
                                raise Exception("DBUpgrader.commit_step: Exception executing post statement:\n" + str(e) + "\nSQL:\n" + _curr_SQL)
                
                
       
    def add_to_application(self,_ApplicationGUID, _Name, _Description):
        """Add an application till the application list table"""
        _insert = SQL_XML().xml_file_to_sql(os.path.normpath(DBUpgrader_XML_Dir_abs + '/insert_application.xml'), 
        ApplicationGUID = _ApplicationGUID, Name=_Name, Description =_Description)
        tmpSQL = _insert.as_sql(self.dal.db_type)
        try:
            self.dal.execute(tmpSQL)
        except Exception as e:
            raise Exception("DBUpgrader.add_to_application: Exception executing statement:\n" + str(e) + "\nSQL:\n" + tmpSQL)
    
       
    def upgrade(self, _ApplicationGUID, _ApplicationName, ApplicationDescription, _Steps, _fromStep = None, _tostep = None):
        """Perform a database upgrade"""
        if _ApplicationGUID == "": raise Exception("DBUpgrader.commit_step: An ApplicationGUID is required.")
       
        # If starting from scratch, add the application to the __application table.
        # Exclude the DBUpgrader itself, that does this in it's creating script's first step.
        if _fromStep == 0 and _ApplicationGUID != '{5113f800-c87b-11df-afd4-0002a5d5c51b}':
            self.add_to_application(_ApplicationGUID, _ApplicationName, ApplicationDescription)
                   
        import sys            
        # Loop steps.
        for _step in _Steps:
            _StepId, _StepGUID, _StepDescription, _Statements = self.get_step_nodes(_step)

            if int(xml_get_text(_StepId)) > _fromStep:
                print("Step description: " + xml_get_text(_StepDescription))
                
                
                sys.stdout.write("Running upgrade step " + xml_get_text(_StepId) + "...")
                
                self.commit_step(_Statements)
                print("..done.")
                # Write to log
                self.write_step_log_entry(xml_get_text(_StepId), xml_get_text(_StepGUID), xml_get_text(_StepDescription), _ApplicationGUID)
          
                
                
        # Perform upgrade
        #  if (_maxstep_File > _step_DB):
        #      UpgradeRange(_step_DB + 1, _maxstep_File, _stepsNode)
            
        pass;   
    
    def upgrade_upgrader(self):
        """If needed, upgrader the structure for the database upgrader"""
        
        # Check for versioning support.
        
        if len(Meta_Queries(self.dal).table_info('__StepLog')) == 0:
            # Assume that database should be created from the beginning(since the first thing should be versioning)..
            _Startstep = 0
            print('DBUpgrader.upgrade_upgrader: No __StepLog database table detected, assuming that DBUpgrader is not installed. Will now install.')
        else:
            # Find the current step in the database.
            _Startstep = self.read_last_step_log_entry(DBUpgrader_GUID)          
            
        # Parse file
        _UpgraderStep, _ApplicationGUID, _ApplicationName, _ApplicationDescription,_Steps, _LastStepGUID, _LastStep = self.get_xml_meta_info(os.path.normpath(DBUpgrader_XML_File_abs))
        
        # Is it supported?
        self.check_upgrader_version(_UpgraderStep)
        
        if _LastStep > _Startstep:
            # Perform upgrade
            print('DBUpgrader.upgrade_upgrader: Upgrading from '+ str(_Startstep) +' to ' + str(_LastStep) + '...')
            self.upgrade(DBUpgrader_GUID, _ApplicationName, _ApplicationDescription, _Steps, _fromStep=_Startstep)
            print('DBUpgrader.upgrade_upgrader: upgrade done. New DBUpgrader database step is ' + str(_LastStep) + '.')
            
    



    def upgrade_database(self, _XML_File):
        """If needed, upgrade the database"""
        
        # First, make sure that the upgrader infrastructure is in place and updated.
        self.upgrade_upgrader()
       
        # Parse xml file
        _UpgraderStep, _ApplicationGUID, _ApplicationName, _ApplicationDescription, _Steps, _LastStep, _LastStep = self.get_xml_meta_info(_XML_File)
        self.ApplicationGUID = _ApplicationGUID
        self.ApplicationName = _ApplicationName
        self.ApplicationDescription = _ApplicationDescription
        
        
        print ("ApplicationGUID : " + _ApplicationGUID)

        # Find the current step in the database.
        _DBStep = int(self.read_last_step_log_entry(_ApplicationGUID))          

        # Perform upgrade.
        if int(_DBStep) < int(_LastStep):
            print('DBUpgrader.upgrade_database: Upgrading from '+ str(_DBStep) +' to ' + str(_LastStep) + '...')
            self.upgrade(_ApplicationGUID, _ApplicationName, _ApplicationDescription, _Steps, _DBStep, _LastStep)
            print('DBUpgrader.upgrade_database: upgrade done. New '+ self.ApplicationName + ' database step is ' + str(_LastStep) + '.')
        else:
            print ("DBUpgrader: Nothing to do.")           

