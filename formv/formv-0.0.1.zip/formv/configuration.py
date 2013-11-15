#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import os, yaml
from pkg_resources import resource_filename as rn   #@UnresolvedImport #pylint: disable=E0611
from formv.utils import dict_object

__all__ = ('build','BaseCountry',)

def build(config_root=None, countries={}):
    """ 
    Formv configuration build. It includes configuration for countries, states
    postcodes, languages, currencies that can be updated to include additional 
    countries. Currently only USA-related configuration is available.
    
    Parameters as follows:
    
    config_root:
        Path to alternative configuration folder. The folder must contain a 
        'config' folder with the actual configuration. See formv/config for
        the folder structure
    countries:
        Callables for geographic configuration. See an explanation below.
    
    By default, build() method is creating the configuration using YAML files  
    available in formv/config folder. Considering that configuration is kept  
    in memory, if it includes many countries and/or their postcodes, the amount 
    of memory required can grow very fast (for instance the file holding USA 
    postcodes has ~44000 lines). Below is an example:
    
    {'countries': {'USA': {'code': 'USA',
                           'currencies': ('USD',),
                           'formats': {'phone': ('+1 # #### ####', 
                                                 '0# #### ####'),
                                       'postcode': ('#####',)},
                           'languages': ('ENG',),
                           'name': 'U.S.A.',
                           'names': ('U.S.A.', 'USA', 'U.S.', 'US', 
                                     'United States of America'),
                           'phone_code': '+1',
                           'postcodes': {'99501': ('61.216799', '-149.87828'),
                                         '99502': ('61.153693', '-149.95932'),
                                         '99503': ('61.19026', '-149.89341'),
                                         '99504': ('61.204466', '-149.74633'),
                                         ...},
                           'states': {
                               'AK': {'code': 'AK',
                                      'names': ('AK', 'Alaska'),
                                      'postcodes': {
                                          '99501': ('61.216799', '-149.87828'),
                                          '99502': ('61.153693', '-149.95932'),
                                          '99503': ('61.19026', '-149.89341'),
                                          '99504': ('61.204466', '-149.74633'),
                                          ...}},
                               'AL': {'code': 'AL',
                                      'names': ('AL', 'Alabama'),
                                      'postcodes': {
                                          '35004': ('33.606379', '-86.50249'),
                                          '35005': ('33.592585', '-86.95969'),
                                          '35006': ('33.451714',  '-87.23957'),
                                          ...}}}}},
     'currencies': {'USD': ('USD', '$', 'Dollar', 'American Dollar')},
     'languages': {'ENG': ('English', 'Eng')}}
     
    Alternatively, you may use callables and store the geographic configuration
    in a database. See an example below:
    
    from formv.configuration import build, BaseCountry
    from formv.utils import dict_object
    
    class Country(BaseCountry):
        def __init__(self, code):
            BaseCountry.__init__(self) 
               
            c = <get country from db using code>    
                                    
            self.code = c.code
            self.name = c.name
            self.names = c.names                           # - (list, tuple)
            self.languages = c.languages                   # - (list, tuple)
            self.currencies = c.currencies                 # - (list, tuple)
            self.phone_code = c.phone_code
            self.formats.phone = c.formats.phone           # - (list, tuple)
            self.formats.postcode = c.formats.postcode     # - (list, tuple)
            self.postcodes = self.Postcodes(country=c.code)        
            self.states = self.States(country=c.code)

        class Postcodes(BaseCountry.Postcodes):
            ''' country level postcodes '''
            def get(self, postcode):
                <return postcode from db> ...
                
            def items(self):
                <iterate postcodes from db cursor> ...
            
            iteritems = items
                                
        class States(BaseCountry.States):
            def get(self, state):
                <return state from db> ...
                
            def items(self):
                <iterate states from db cursor> ...
            
            iteritems = items

            class Postcodes(object):
                ''' state level postcodes '''
                def get(self, postcode):
                    <return postcode from db> ...
        
                def items(self):
                    <iterate postcodes from db cursor> ...
                    
                iteritems = items
                
    formv.config = build(countries={'USA': Country('USA'), ...})

    For more details see tests/__init__.py and tests/test.py
    """
    def get_resource(resource_name, config_root=config_root):
        if config_root:
            resource = os.path.abspath(os.path.join(config_root, resource_name))
            assert os.path.isfile(resource), 'Resource not found: %s' % resource
            return resource
        return rn('formv', resource_name)
    
    if countries:
        for c in countries.values():                
            assert isinstance(c, BaseCountry)

    conf = configuration(files=(get_resource('config/config.yaml'),))    
    for k in conf:
        cfg_file = get_resource('config/files/%s.yaml' % k)
        conf[k] = configuration(files=(cfg_file,))
    
    for k in conf.countries:
        if k in countries:
            conf.countries[k] = countries[k]
        else:  
            countries_base = 'config/files/countries/'
            country_f = get_resource((countries_base + '%s.yaml') % k)
            conf.countries[k] = configuration(files=(country_f,))
            
            states_f = get_resource((countries_base + 'states/%s.yaml') % k)
            if os.path.isfile(states_f):            
                conf.countries[k].states = configuration(files=(states_f,))

            postcodes_f = get_resource((countries_base + 'postcodes/%s.yaml') % k)
            if os.path.isfile(postcodes_f):            
                conf.countries[k].postcodes = configuration(files=(postcodes_f,))
            
            states_postcodes_f = get_resource((countries_base + 'states/postcodes/%s.yaml') % k)
            sp = configuration(files=(states_postcodes_f,))
            for s in conf.countries[k].states:                
                conf.countries[k].states[s].postcodes = sp[s]
    return conf


class BaseCountry(object):
    def __init__(self):
        self.code = None
        self.name = None
        self.names = []
        self.languages = []
        self.currencies = []        
        self.phone_code = None
        self.formats = dict_object()
        self.formats.phone = []
        self.formats.postcode = []
        self.postcodes = self.Postcodes(country=self.code)        
        self.states = self.States(country=self.code)
    
    class Postcodes(object):
        """ country level postcodes """
        def __init__(self, country):
            self.country = country
            
        def get(self, postcode):
            raise NotImplementedError

        def items(self):
            raise NotImplementedError
            
        iteritems = items
            
    class States(object):
        def __init__(self, country):            
            self.country = country
            
        def get(self, state):
            raise NotImplementedError
        
        def items(self):
            raise NotImplementedError
        
        iteritems = items
        
        class Postcodes(object):
            """ state level postcodes """
            def __init__(self, country, state):
                self.country = country
                self.state = state
                
            def get(self, postcode):
                raise NotImplementedError
    
            def items(self):
                raise NotImplementedError
                
            iteritems = items
 

class configuration(dict_object):
    def __init__(self, files, *args, **kargs):        
        dict_object.__init__(self, *args, **kargs)
        yaml_files = []
        yaml_data = {}
        
        if isinstance(files, (list, tuple)):
            yaml_files.extend(files)
        else:
            yaml_files.append(files)

        for yf in yaml_files:
            f = open(yf, 'rb')
            try:
                data = yaml.load(f.read())
            finally:
                f.close()
                
            # - checks overlapping keys across files, not at file level
            for k in data.keys():    
                if k in yaml_data:
                    msg = 'Overlapping configuration key: "%s:%s"'
                    raise ValueError(msg % (yf, str(k)))
            yaml_data.update(data)
                     
        self.update(self.build(yaml_data))
    
    def build(self, data):        
        if isinstance(data, dict):
            output = dict_object()
            for key in data:
                output[key] = self.build(data[key])
        elif isinstance(data, (list, tuple)):
            output = []
            for i, key in enumerate(data):                                
                output.append(self.build(data[i]))  
            output = tuple(output)      
        else:
            output = data
        return output