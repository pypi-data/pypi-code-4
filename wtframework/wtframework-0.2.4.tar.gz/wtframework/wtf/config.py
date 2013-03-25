##########################################################################
#This file is part of WTFramework. 
#
#    WTFramework is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    WTFramework is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with WTFramework.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################


from wtframework.wtf.utils.project_utils import ProjectUtils
import os
import re
import yaml


class ConfigReader:
    '''
    Config Reader provides a singleton instance of ConfigReader for looking up 
    values for config variables.
    '''

    CONFIG_LOCATION = 'configs/'
    DEFAULT_CONFIG_FILE = 'default'
    CONFIG_EXT = '.yaml'

    ENV_VARS = "WTF_ENV"

    _dataMaps = None #instance variable to store config data loaded.
    _singleton_instance = None #class variable to track singleton.

    def __init__(self, _env_var_ = None):
        self._dataMaps = []

        #load default yaml file if this is not a unit test.
        try:
            if _env_var_ != None: 
                # We pass in a custom env var for unit testing.
                configs = re.split(",|;", _env_var_)
                for config in reversed(configs):
                    self.__load_config_file(config)
            elif not ConfigReader.ENV_VARS in os.environ:
                raise Exception("No Config Specified, using defaults.")
            else:
                # Read and load in all configs specified in reverse order
                configs = re.split(",|;", str(os.environ[ConfigReader.ENV_VARS]))
                for config in reversed(configs):
                    self.__load_config_file(config)

                
        except Exception as e:
            #Fall back to default.yaml file when no config settings are specified.
            print "An error occurred while loading config file:", e
            print "Falling back to 'default' config."
            self.__load_config_file(ConfigReader.DEFAULT_CONFIG_FILE)


    class __NoDefaultSpecified__(object):
        "No default specified to config reader."
        pass

    def get(self,key, default_value=__NoDefaultSpecified__):
        '''
        Gets the value from the yaml config based on the key.
        
        No type casting is performed, any type casting should be 
        performed by the caller.
        
        @param key: Name of the config you wish to retrieve.  
        @type key: str
        @param default_value: Value to return if the config setting does not exist. 
        '''
        for data_map in self._dataMaps:
            try:
                if "." in key:
                    #this is a multi levl string
                    namespaces = key.split(".")
                    temp_var = data_map
                    for name in namespaces:
                        temp_var = temp_var[name]
                    return temp_var
                else:
                    value = data_map[key]
                    return value                
            except (AttributeError, TypeError, KeyError):
                pass
            
        if default_value == self.__NoDefaultSpecified__:
            raise KeyError("Key '{0}' does not exist".format(key))
        else:
            return default_value


    def __load_config_file(self, file_name):
        config_file_location = os.path.join(ProjectUtils.get_project_root() +
                                            ConfigReader.CONFIG_LOCATION + 
                                            file_name + 
                                            ConfigReader.CONFIG_EXT)
        print "locaing config file:", config_file_location
        config_yaml = open(config_file_location, 'r')
        dataMap = yaml.load(config_yaml)
        self._dataMaps.insert(0, dataMap)
        config_yaml.close()


class ConfigReaderAccessException(Exception):
    '''
    Exception Thrown that should be explicitly caught when trying to 
    manually set the config reader.
    '''
    pass


# Create a global constant for referencing this to avoid re-instantiating 
# this object over and over.
WTF_CONFIG_READER = ConfigReader()



class TimeOutManager(object):
    """
    Utility class for getting default config values for various timeout 
    periods.
    """
    _config = None
    
    def __init__(self, config_reader = WTF_CONFIG_READER):
        "Initializer"
        self._config = config_reader

    @property
    def BRIEF(self):
        "Useful for waiting/pausing for things that should happen near instant."
        return self._config.get("timeout.brief", 5)

    @property
    def SHORT(self):
        """"
        Useful for waiting/pausing for things that are just long enough for a
        brief appearance of a loading indicator. 
        """
        return self._config.get("timeout.short", 10)


    @property
    def NORMAL(self):
        """
        Useful for a normal considerable wait.  Such as waiting for a large page to 
        fully load on screen.
        """
        return self._config.get("timeout.normal", 30)

    @property
    def LONG(self):
        """
        Useful for things that take a long time.  Such as waiting for an moderate size 
        download/upload to complete.
        """
        return self._config.get("timeout.long", 60)

    @property
    def EPIC(self):
        """
        Useful for operations that take an extremly long amount of time.  For example, 
        waiting for a large upload to complete.
        """
        return self._config.get("timeout.epic", 300)



# Default instance of TimeOut Manager for easy access.  You can use this as 
# follows:
#        PageUtils.wait_for_page_to_load(SlowPage, WTF_TIMEOUT_MANAGER.LONG)
#
WTF_TIMEOUT_MANAGER = TimeOutManager()