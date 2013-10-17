"""
This module is responsible for creating the business rules for the CCHR 
conversion system. 

Exported Classes:

Exported Methods:

parse_rules -- This method is called during the stage and process phase to 
create the business rules for that phase. 

Exceptions:

RuleParsingError

ConvertError -- This error is raised when a value we are trying to convert 
can not be handled by a Crosswalk object.

DataError 

FatalDataError
 
"""

import os, imp
from itertools import count, izip
from datetime import datetime
from itertools import izip
from memcache import Client

import cardsharp as cs
import log
from errors import *
from rules import *
from util import *
from snttext import SNTParser
from region import *
import re

_count = count().next

def mod_counter():
    return 'bjs_' + str(_count())

class VariableConverter(object):
    def __init__(self, time, segment, var, stage, halt_on_error):
        self.time = time
        self.func = None
        self.id_count = None
        self.regions = dict()
        self.region_order = []
        self.format_setters = set()
        self.halt_on_error = halt_on_error
        self.segment = segment
        self.var = var
        self.stage = stage
        
    def add_region(self, region, mod, crosswalk):
        if mod:
            self.format_setters.add(mod)
            
        if crosswalk:
            for key in crosswalk.iterkeys():
                self.format_setters.add(crosswalk[key])
                
        self.regions[region] = _get_region_func(self.time, self.segment, 
                                                self.var, self.stage, 
                                                mod, crosswalk, 
                                                self.halt_on_error)
        self.region_order.append(region)
        self.region_order.sort(key = lambda r: r.priority())
        
    def create_func(self, mod, crosswalk):
        if mod:
            self.format_setters.add(mod)
            
        if crosswalk:
            for key in crosswalk.iterkeys():
                self.format_setters.add(crosswalk[key])
            
        self.func = _get_region_func(self.time, self.segment, self.var, 
                                     self.stage, mod, crosswalk, 
                                     self.halt_on_error)
    
    def set_format(self, format):
        for rs in self.format_setters:
            rs.format = format
    
    def set_auto_id(self, start_value=1):
        #TODO put this rule in loader
        """This modules sets the translate function to pass an id value to the conversion function. The first id
        will start at **start_value**, which has a default value of 0, and will increment by one for each row.""" 
        self.id_count = count(start_value).next
    
    def translate(self, state, value, row):
        #if regions are specified then loop over them and return the region specfic function
        for region in self.region_order:
            #TODO pass in map of rules to get 1 iteration over dataset
            if row[state].lower() in region.get_state():
                try:
                     if self.id_count is not None:
                         return self.regions[region](self.id_count())  
                     else:
                         return self.regions[region](value, row)
                    
                except ConvertError:
                    if cs.config.debug:
                        raise
                    else:
                        #TODO ADD LOGGING
                        pass
        
        #no regions are specified than return global function
        if self.id_count is not None:
            return self.func(self.id_count())         
        else:
            return self.func(value, row)

def _get_region_func(time, seg, var, phase, mod, crosswalk, error):
    #pass objects to mod
    mod.log = log.Log(time = time, segment = seg, var = var, phase = phase)
    mod.ConvertError = ConvertError
    mod.RuleError = cs.rules.RuleError
    mod.DataError = DataError
    mod.FatalDataError = FatalDataError
    mod.halt_on_error = error
    mod.regions = regions
    mod.clean_key = clean_key
    mod.default_offense_codes = [9999, 999, None, 9, 9, 99, 9]
    mod.o_vars = ['ncic', 'chg', 'inc', 'dom', 'weap', 'cdv', 'pg']
    mod.vars = {}
    mod.re = re
    mod.izip = izip
    
    mc = Client(['127.0.0.1:11211'], debug=0)
    #if phase == '1':
    #    mc.flush_all()
    mod.mc = mc
    
    if mod and crosswalk:
        mod.crosswalk = crosswalk
            
    if mod:
        if hasattr(mod, 'convert'):
            def func(value, row):
                try:
                    return mod.convert(value, row)
                #handle type ecpetion for easier debugging
                except TypeError as err:
                    raise ConvertError("""Unable to call convert on var %s, %s""" % (var, err))
            return func
        
        elif hasattr(mod, 'assign_vals'):
            def func(value, row):
                snt_processor = SNTParser(row, mod.log)
                return mod.assign_vals(value, row, snt_processor)
            
            return func
        
        elif hasattr(mod, 'translate'):
            def func(value, row):
                return mod.translate(value)
            
            return func
        
        elif hasattr(mod, 'assign_id'):
            def func(value):
                return mod.assign_id(value)
            
            return func
        
        elif hasattr(mod, 'validate'):
            return mod.validate
        
    elif crosswalk:
        def func(key, value, row):
            return crosswalk[key].convert(value)
             
        return func
        
    else:
        raise RuleParsingError()
    
def parse_rules(rule_dir, db_info, stage, halt_on_error = False):
    #TODO: change db_info['name'] to 'filename' to allow db_info to be passed as keyword
    time = datetime.now().isoformat('_').replace(':', '-')
    _seg_map, _var_map, vars = {}, {}, {}
    segments = cs.load(source=os.path.join(db_info['dir'], '..','segments.xls'), 
                       format='excel')
    #variables = cs.load(source=db_info['name'], dataset='variables', 
    #                    format='mysql', user=db_info['user'], 
    #                    pwd=db_info['pass'])
    variables = cs.load(source=db_info['name'], dataset='variables', 
                        format='mongo', var_names = [('_id', 'integer'), 
                        ('segment_id', 'integer'), ('index_', 'integer'), 
                        'label', ('original', 'integer'), 
                        'format', ('length', 'integer'), 
                        ('percision', 'integer'), ('original', 'boolean'), 
                        ('current', 'boolean')])
    
    segments['id'].convert('integer')
    
    cs.wait()
    for row in segments:
        _seg_map[row['label'].lower()] = row['id']
    for row in variables:
        _var_map[row['label'].lower()] = (row['_id'], row['format'])
    
    #for each segment
    #loop over segment directories (arrest, demographic, sentence, supervision)
    for segment_dir in os.listdir(rule_dir):
        segment_name = segment_dir.lower()
        segment_dir = os.path.join(rule_dir, segment_dir)
        if os.path.isfile(segment_dir):
            continue #if file than not a segment directory, check next
        
        #for each variable
        #loop over all variable folders within a segment
        for var_dir in os.listdir(segment_dir):
            var_name = var_dir.lower()
            var_dir = os.path.join(segment_dir, var_dir)
            
            if os.path.isfile(var_dir):
                continue #if file than not a variable directory, check next
            
            #create a variable converter
            vc = VariableConverter(time, _seg_map[segment_name], _var_map[var_name][0], stage, halt_on_error)
            vc_mod = None
            vc_crosswalk = dict()
            
            #for each rule or region
            #loop over all files in the variable directory
            for filename in os.listdir(var_dir):
                full_path = os.path.join(var_dir, filename)
                
                #load crosswalk rule
                if filename.startswith('crosswalk'):
                    print 'Loading crosswalk for %s' % filename
                    if filename[len(filename) - 4:len(filename)].lower() != '.txt':
                        raise RuleParsingError('file type must be .txt not %s' % 
                                               filename[len(filename) - 4:len(filename)])
                    vc_crosswalk[filename[10:len(filename) - 4].lower()] = Crosswalk(full_path, db_info)
                
                #load func rule
                elif filename == 'func.py':
                    print 'Loading functions for %s' % var_name
                    vc_mod = imp.load_source(mod_counter(), full_path)
                elif filename.endswith('.pyc'):
                    pass                               
                #load region rules
                elif os.path.isdir(full_path):
                    region = get_region(filename)
                    
                    crosswalk = dict()
                    mod = None
                    
                    #for each rule
                    for filename in os.listdir(full_path):
                        file_path = os.path.join(full_path, filename)
                        filename = filename.lower()
                        
                        #load region crosswalk
                        if filename.startswith('crosswalk'):
                            print 'Loading crosswalk for %s' % var_name
                            if filename[len(filename) - 4:len(filename)].lower() != '.txt':
                                raise RuleParsingError('file type must be .txt not %s' % 
                                                       filename[len(filename) - 4:len(filename)])
                            crosswalk[filename[10:len(filename) - 4].lower()] = Crosswalk(file_path, db_info)
                        #load func rule
                        elif filename == 'func.py':
                            print 'Loading functions for %s:%s' % (var_name, region)
                            mod = imp.load_source(mod_counter(), file_path)
                        elif filename.endswith('.pyc'):
                            pass
                        else:
                            raise RuleParsingError('Region directory %s for var %s can only contain "crosswalk.txt", or "func.py" files.  Found: %s' % (region, var_name, filename))
                    
                    #add region rules to variable converter
                    #pass segment_name for log output
                    #region used for log and to store region func / crosswalk
                    #func is the function to be associated with the  converter
                    #crosswalk is the crosswalk to be used by the  converter (in addition to func or standalone) 
                    vc.add_region(region, mod, crosswalk)
                else:
                    raise RuleParsingError(' directory %s can only contain region directories, "func.py" files, or "crosswalk.txt" files.  Found: %s' % (var_name, filename))
           
            #create variable rule
            vc.create_func(vc_mod, vc_crosswalk)
            
            vars[(segment_name, var_name)] = vc
    
    return vars