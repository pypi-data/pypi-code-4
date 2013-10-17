import re
from ..errors import *
from ..util import re_escape, calc
__all__ = ['Rule', 'CopyRule', 'RegexRule', 'RegexMathRule']

class Rule(object):
    """Generic Rule class which returns a list of values. 
    A Rule will be added to the RuleSet.rules dict. When a Transform task is created using
    a given RuleSet the input_key will be checked to see if it is in the RuleSet.rules dict.
    If it is then the result will be returned.
    
    @param intial: A string defining the initial value of the rule. The initial result
                   will be compared against a value in the data. If the initial matches
                   the value in the data result will be returned.
    @param result: A list of values to be returned by the convert function.
    @return: result
     
    
    Public Methods:
    convert -- Returns the result 
    """
    def __init__(self, initial, result, metadata):
        self.initial = initial
        self.result = result
        self.metadata = metadata
        self.validate()
        
    def validate(self):
        #TODO add Format validation between result and out_vars
        if self.initial is None:
            if self.metadata.type not in ['none', 'all', 'copy']:
                raise TransformRuleError("None value not allowed for Rule when metadata.type != 'none' or 'all' or 'copy'.")
        #TODO add smart creation of intial (if given a iterable create a string
        elif not isinstance(self.initial, basestring):
             raise TransformRuleError("Initial value must be a string")
            
    def convert(self):
        return self.result

class CopyRule(Rule):
    """Copy the in_var into the out_vars. 
    One input var can be mapped to 1 or more output vars."""
    def __init__(self, result, metadata):
        """
        @param result: The variable to copy to the out_vars
        """
        self.initial = None
        #TODO add validation to make sure variable specified is in dataset
        self.result = result
        self.metadata = metadata
        self.validate()
    
    def validate(self):
        #TODO add Format validation between result and out_vars
        if len(self.metadata.in_vars) > 1:
            raise TransformRuleError("CopyRule can only have one in_var.")
    
    def convert(self, row):
        value = row[self.metadata.in_vars[0].name]
        return [value for v in self.metadata.out_vars]
    
class RegexRule(Rule):
    def __init__(self, intial, result, metadata):
        """
        @param initial: A regular expression pattern
        @param result: The value to be returned if the regular expression matches
        #TODO better doc
                     math: return match object groups applied to math function
                     search: return re.search
                     match: return re.match
        """
        #escape intial as needed
        self.metadata = metadata
        
        if self.metadata.escape:
            '''# captures '#' or '#\d+' or '\d+' '''
            self.regex = re_escape(intial).replace('#', '(\d+|#\d+|#)') 
        else:
            self.regex = intial
        
        if self.metadata.type == 'search':
            self.re_func = re.search
        elif self.metadata.type == 'match':
            self.re_func = re.match
        elif self.metadata.type == 'exact': 
            self.regex = ''.join([self.regex, '$'])
            self.re_func = re.match
        
        self.regex = re.compile(self.regex, re.I) #actual regular expression string
            
        self.result = result
        self.initial = intial
        self.groups = None #object to hold groups result
        self.validate()
    
    def validate(self):
        #TODO add Format validation between result and out_vars
        if self.metadata.type not in ['search', 'match', 'exact']:
            raise TransformRuleError("RegexRule must be of metadata.type (search, match, or exact).")
        
    def handle(self, value):
        """Returns True if rule can handle the value. Convert will only be called 
        if handle returns True."""
        return self.re_func(self.regex, value)
    
class RegexMathRule(RegexRule):
    def handle(self, value):
        RegexRule.handle(self, value)
        
        match = self.re_func(self.regex, value)

        if match:
            self.groups = match.groups()
            return True
        else:
            return False

    def convert(self, **kw):
        """
        Currently only supports capturing integers.
        
        TODO: add support for named groups
        TODO: add support for capturing floats
        
        For math regex apply groups extracted from value to arthimetic function within self.result
        Math:
        >>> r = RegexMathRule('Sent to #Day #Y', '#1 + #2(365.25)', 'math')
        >>> r.handle('Sent to 10Day 2Y')
        True
        >>> r.convert()
        740.5
        """
        #groups are base 0, research tema has been entering there # objects as base one
        #subtract 1 from every #\d+ match and return the matched group
        #example) 
        #   regex = Sent to #Day #Y
        #   result = #1 + #2(365.25)
        #    value = 'Sent to 10Day 2Y'
        #return calc('10 + 2(365.25)')
        
        try:
            results = [r if r else 'None' for r in self.result.split(kw['split'])]
            return [calc(re.sub('(#)(\d+)', lambda c: self.groups[int(c.group(2)) - 1].replace('#', ''), str(x))) for x in self.result]
            
        except IndexError:
            raise TransformRuleError("Invalid output value: key:%s | value:%s, number index out of range" % (self.regex.pattern,str(self.result)))
        except SyntaxError:
            raise TransformRuleError("Syntax Error: check rule syntax: key:%s | value:%s" % (self.regex.pattern,str(self.result)))
        
class RegexReturnRule(RegexRule):
    """Return the Match Object of a match regular expression.
    
    TODO: think about if this should be included. Maybe this should take a funciton
    and apply the function to the MatchObject?
    TODO: add testing when finished
    """
    def __init__(self, initial, result, metadata):
        RegexRule.__init__(self, initial, result, metdata)
            
    def handle(self, value):
        RegexRule.handle(self, value)  
        self.result = self.re_func(self.regex, value) 
        
        return True if self.result else False 

class Lookup(object):
    def __init__(self, db, tables):
        self.values = []
        for table in tables.split('|'):
            ds = cs.load(source=db['name'], format='mysql', dataset=table, 
                         user=db['user'], pwd=db['pass'])
            self.values.append(([row['id'] for row in ds], table))

    def validate(self, initial, value, filename):
        #iterate over all values and lookups checking to see if each value
        #in corresponding lookup list
        temp_value = value.split('|')
        
        for v, l in izip(temp_value, self.values):
            if v not in ['', 'None'] and int(v) not in l[0]:
                log.write('rule_init', [v, l[1], l[0], filename, str(self.values), 'Value not present in lookup'])
                return False
    
        return True