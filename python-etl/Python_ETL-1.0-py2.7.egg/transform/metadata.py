
from ..errors import *
from .RuleController import *
from .util import *
 
__all__ = ['LogMetadata', 'RuleManagerMetadata', 'RuleSetMetadata', 'RuleMetadata',
           'RuleControllerMetadata', 'KeyMetadata']

class RuleManagerMetadata(object):
    def __init__(self, priority=1, rule_filter=None):
        self.rule_filter = rule_filter
        self.priority = priority
        self.validate()
        
    def validate(self):
        if self.rule_filter and not isinstance(self.rule_filter, Filter):
            raise TransformError('Filter must be of type Filter.')

class RuleControllerMetadata(object):
    def __init__(self, priority=1, filter_value=None):
        self.filter_value = filter_value
        self.priority = priority

class RuleSetMetadata(RuleControllerMetadata):
    #TODO: need to add math as a value to metadata
    #TODO: restructure using *args, **kw
    def __init__(self, key_meta, out_vars, filter_value=None, priority=1, **kw):
        """
        @param key_meta: A list of KeyMetadata objects. This list is used in get_key method to create the default key for the RuleSet. 
                         The creation of a key can be specified at the rule level by overriding key_meta using RuleMetadata(add link).
        #TODO have out_vars be similar to key_meta to allow for a transform function to be applied to the out_variable
        @param out_vars: A VariableSet(add link) containing Variable information to specify the Variables the Rule will update.  out_vars can be overridden by RuleMetadata(add link).
        @param kw-missing: Provide a list for missing values. By default a list of None values created to with the length equal to length of out_vars. 
        @param kw-unknown: Provide a list for unknown values. By default a list of None values created to with the length equal to length of out_vars.
        @param kw-log: Specify a log to enable logging on this rule. This will override the RuleSet log.
        @param kw-key_trans_map: a dict mapping of in_var name to a function. Function will be applied to in_var during construction of key. 
        @param type: Specify a type if rule is anything other than a generic Rule ie(noneRule, allRule).
        @param escape: For regex rules specify escape = False to not escape the regex
        @param force_unknown: If set to True will force the ruleset to try and code unknown values when applicable (overwrite not set).
        """
        RuleControllerMetadata.__init__(self, priority, filter_value)
        self.key_meta = key_meta #formally called in_vars
        self._key_map = dict([(key.name, key) for key in self.key_meta])
        self.out_vars = out_vars
        self.keywords = kw
        self.missing = kw.get('missing')
        self.unknown = kw.get('unknown')
        self.predicate = kw.get('predicate')
        self.log = kw.get('log')
        self.all_rule = False
        self.copy_rule = False
        self.force_unknown = kw.get('force_unknown')
        self.validate()
    
    @property
    def keys(self):
        return self._key_map
    
    def get_key(self, row, as_str=False, delimiter='|'):
        #TODO add unit test
        """Get the ruleset key for a particular row in the dataset.
        
        @param row: A row object of a cardsharp dataset
        @return: Returns a list of transformed keys based on KeyMetadata in key_meta 
        @param as_str: Set to True to force the returned object to be a string instead of a list. The string is joined on delimiter keyword. Default is False (turned off)
        @param delimiter: The string the returned object will joined on if as_str = False. Default is '|' 
        """
        return [key.get_key(row) for key in self.key_meta] if not as_str else '%s' % delimiter.join([key.get_key(row) for key in self.key_meta])
        
    #TODO add setter for missing and unknown to call validate when set
    
    def validate(self):
        if self.missing and (len(self.missing) != len(self.out_vars)):
            raise TransformRuleError('RuleSetMetdata must have same number of missing values as out_vars')
        if self.unknown and (len(self.unknown) != len(self.out_vars)):        
            raise TransformRuleError('RuleSetMetdata must have same number of unknown values to out_vars')
         

class RuleMetadata(RuleSetMetadata):
    def __init__(self, type=None, escape=False, in_vars=None, out_vars=None, **kw):
        """
        Each individual Rule has its own metadata. By default the metadata matches the RuleSet metadata. 
        
        @param in_vars: A VariableSet(add link) containing Variable information to construct all Rule keys. If supplied this will override the RuleSet in_vars.
        @param out_vars: A VariableSet(add link) containing Variable information to specify the Variables the Rule will update. If supplied this will override the RuleSet in_vars.
        @param log: Specify a log to enable logging on this rule.
        @param missing: Provide a list for missing values. This list should map to out_vars. 
        @param unknown: Provide a list for unknown values. This list should map to out_vars.
        
        """
        RuleSetMetadata.__init__(self, in_vars, out_vars, **kw)
        self.type = type
        self.escape = escape
        self.priority = kw.get('priority')

class KeyMetadata(object):
    def __init__(self, variable, order, **kw):
        """Metadata for a key object. 
        @param variable: A Cardsharp Variable object the key maps to.
        """
        self.name = variable.name
        self.format = variable.format
        self.order = order
        self.as_str = kw.get('as_str', False)
        self.inner_trim = kw.get('as_str', False)
        
        def _transform(key, **kw):
            return key
        
        self.transform = kw.get('transform', _transform)
         
    
    def get_key(self, row, func=None, **kw):
        """Function returns a key based on values in the row object. The default behavior is to 
        simply return the row value of the variable passed to the KeyMetadata object during initialization. 
        If the as_str attribute is set to True than we use the key_as_str object to create the key if the 
        func parameter is None. The key_as_str object will be passed the inner_trim attribute. 
        If a function is passed to func this is used. The func will be passed the row and the **kw dictionary   
        Finally the key will be transformed using the function using the funciton stored in transform attribute.
         
        @param row: Required row arguement that contains the data from which we will make a key.
        @param func: Optional, a function to be used to create a key. This function will be passed 
                     the row object and **kw dictionary.  
        """
        #get the key and transform it
        if self.as_str:
            if not func:
                _key = key_as_str(row[self.name], inner_trim=self.inner_trim)
            else:
                _key = key_as_str(func(row, **kw), inner_trim=self.inner_trim)
            
            #pass the name so we can know which key to lookup in the crosswalk, this allows multiple transforms
            return key_as_str(self.transform(_key, var_name=self.name), inner_trim=self.inner_trim)
         
        elif func:
            return self.transform(func(row[self.name], **kw))
        else:
            return self.transform(row[self.name])

class KeyMetadataSet(object):
    def __init__(self, keys=()):
        """Creates a collection of KeyMetadata objects.
        
        >>> VariableSet([u'a', u'b', u'c'])
        VariableSet([Variable(u'a', u'string'), Variable(u'b', u'string'), Variable(u'c', u'string')])
        >>> VariableSet([(u'a', u'integer'), u'b', u'c'])
        VariableSet([Variable(u'a', u'integer'), Variable(u'b', u'string'), Variable(u'c', u'string')])
        >>> VariableSet([Variable(u'a', format = u'boolean'), u'b', u'c'])
        VariableSet([Variable(u'a', u'boolean'), Variable(u'b', u'string'), Variable(u'c', u'string')])
        >>> VariableSet([(u'a', u'x', u'y'), u'b', u'c'])
        Traceback (most recent call last):
            ...
        CardsharpError: Cannot use (u'a', u'x', u'y') in Variable listing
        >>> VariableSet([u'a', u'a', u'a'])
        Traceback (most recent call last):
            ...
        CardsharpError: Duplicate variable declaration: a
        """
        
        self._keys = []
        self._mapping = dict()
        for k in keys:
            k = self._make_key(k)
            
            if k.name in self._mapping:
                raise CardsharpError('Duplicate key declaration: %s' % k.name)
            
            k._set = self
            self._keys.append(k)
            
            self._mapping[k] = k
            self._mapping[k.name] = k

        self._data = None
         
#TODO get logging working
class LogMetadata(object):
    def __init__(self, name, vars, message):
        self.name = name
        self.vars = vars
        self.message = message


