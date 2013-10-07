# Copyright (c) 2010 NORC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division, unicode_literals, absolute_import

__all__ = ['option', 'saves', 'loads', 'after', 'get_options', 'option_module', ]

INITIAL_STAGE = 'initial'
VARIABLES_STAGE = 'variables'

from ..errors import *
from ..util import NOT_DEFINED
from .. import config
from . import LOADING, SAVING

from functools import wraps
from collections import defaultdict, Sequence
from itertools import izip_longest
import re, os

def lower(s):
    return s.lower()

_all_options = defaultdict(set)
_current_module = None

def option_module(module):
    class OptionModule(object):
        def __enter__(self):
            global _current_module
            self._old_current_module = _current_module
            _current_module = module
            return self
        
        def __exit__(self, ex_type, ex_value, ex_tb):
            global _current_module
            _current_module = self._old_current_module

    return OptionModule()

def get_options(module, mode):
    options = dict()
    
    def check_option(opt):
        if hasattr(opt, 'saves'):
            for_save = getattr(opt, 'saves')
            for_load = getattr(opt, 'loads', False)
        elif hasattr(opt, 'loads'):
            for_load = getattr(opt, 'loads')
            for_save = False
        else:
            for_save = True
            for_load = True
        
        if mode == LOADING and for_load:
            options[opt.__name__] = opt
        elif mode == SAVING and for_save:
            options[opt.__name__] = opt
        elif not (for_load or for_save):
            raise CardsharpError('Option invalid for both loading and saving: %r' % opt)
        
    for opt in _all_options['cardsharp.drivers.options']:
        check_option(opt)
        
    for opt in _all_options[module]:
        if isinstance(opt, basestring):
            options.pop(opt, None)
        else:
            check_option(opt)
        
    options = options.values()
    total, handled, final_options = len(options), set(), []
    while options:
        for opt in list(options):
            after = getattr(opt, 'after', [])
            if all(name in handled for name in after):
                handled.add(opt.__name__)
                final_options.append(opt)
                options.remove(opt)
        
        if len(options) == total:
            opt = options[0]
            raise CardsharpError('Unable to find precursors for option %s (requires %s)' % (opt.__name__, ', '.join(str(s) for s in opt.after)))
        
        total = len(options)
    
    return final_options
    
def option(convert = None, default = NOT_DEFINED, required = False, stage = INITIAL_STAGE, delete = False):
    def _func(func):
        name = func.__name__
        
        @wraps(func)
        def _exec(options):
            if delete:
                if name in options:
                    raise OptionError('%s is not a valid option for %s' % (name, (_current_module or func.__module__)))
                else:
                    options[name] = None
                    
            if required and name not in options:
                raise OptionError('%s is a required option' % name)
            
            if default is not NOT_DEFINED:
                options.setdefault(name, default)
                
            if convert and name in options:
                if options[name]:
                    options[name] = convert(options[name])

            func(options)
        
        _all_options[_current_module or func.__module__].add(_exec)
        _exec.name = name
        _exec.stage = stage
        _exec.delete = delete
        
        return _exec
    
    return _func
    
def saves(func):
    func.saves = True
    return func

def loads(func):
    func.loads = True
    return func

def after(*args):
    def _func(func):
        func.after = set(args)
        return func
    
    return _func

@loads
@option(required = True)
def source(options):
    f = options['source']
    if f and not os.path.exists(f):
        raise OptionError('File %s does not exist' % f)
    
@saves
@after('overwrite')
@option(required = True)
def source(options):
    f = options.get('source')
    if f and not options.get('dataset') and not options.get('overwrite') and os.path.exists(f):
        raise OptionError('File %s exists, but overwrite is not set' % f)

@saves
@option(convert = bool)
def overwrite(options):
    options.setdefault('overwrite', config.overwrite)

@saves
@after('overwrite')
@after('update')
@option(convert = bool)
def append(options):
    pass
    
@saves
@after('overwrite')
@option(convert = bool)
def update(options):
    pass

@saves
@after('overwrite')
@option(convert = bool)
def replace(options):
    pass

@saves
@after('update')
@option(required = False)
def where(options):
    pass

@option(required = True)
def dataset(options):
    pass

@option(required = False)
def encoding(options):
    pass

@option(required = False)
def delimiter(options):
    pass

@loads
@option(required = False)
def var_names(options):
    pass

@loads
@option(required = False)
def length_rules(options):
    """Allow the user to add length variable rules to the dataset when 
    calling the load command. Rules are assigned before data is loaded."""
    if options.get('length_rules'):
        if not isinstance(options['length_rules'], dict):
            raise LoadError("Length rules option must be a dictionary")

@loads
@option(required = False)
def scale_rules(options):
    """Allow the user to add scale variable rules to the dataset when 
    calling the load command. Rules are assigned before data is loaded."""
    if options.get('scale_rules'):
        if not isinstance(options['scale_rules'], dict):
            raise LoadError("Scale rules option must be a dictionary")

@loads
@option(required = False)
def precision_rules(options):
    """Allow the user to add precision variable rules to the dataset when 
    calling the load command. Rules are assigned before data is loaded."""
    if options.get('precision_rules'):
        if not isinstance(options['precision_rules'], dict):
            raise LoadError("Precision rules option must be a dictionary")
        
@loads
@option(required = False)
def not_null_rules(options):
    """Allow the user to specify which varaibles should not be null when
    calling the load command. The format would be var_name:True .
    Rules are assigned before data is loaded."""
    
    if options.get('not_null_rules'):
        if not isinstance(options['not_null_rules'], dict):
            raise LoadError("Not Null rules option must be a dictionary")  
        
@option(required = False)
def collate(options):
    pass

@option(convert = lower)
def format(options):
    pass

@option()
def handler(options):
    pass

@option(convert = int)
def limit(options):
    ''' Limit to only *x* number of rows when saving or loading where *x* is the value of *options['limit']*. 
    OptionError raised if *options['limit']* < 1. 
    
    >>> import cardsharp as cs
    >>> from cardsharp.test import get_temp_file
    >>> ds = cs.Dataset(['a', 'b', 'c'])
    >>> ds.wait()
    >>> for x in range(100):
    ...     ds.add_row([unicode(x), unicode(x), unicode(x)])
    >>> with get_temp_file('txt') as temp:
    ...     ds.save(source = temp.name, format='text', limit='10', encoding='utf-8')
    ...     ds.wait()
    ...     d1 = cs.load(source = temp.name, format='text', encoding='utf-8')
    ...     d1.wait()
    ...     assert len(d1.rows) == 10
    ...     for x in d1:
    ...         x
    Row([u'99', u'99', u'99'])
    Row([u'98', u'98', u'98'])
    Row([u'97', u'97', u'97'])
    Row([u'96', u'96', u'96'])
    Row([u'95', u'95', u'95'])
    Row([u'94', u'94', u'94'])
    Row([u'93', u'93', u'93'])
    Row([u'92', u'92', u'92'])
    Row([u'91', u'91', u'91'])
    Row([u'90', u'90', u'90'])
    '''
    if 'limit' in options:
        if options['limit'] < 1:
            raise OptionError('Limit cannot be less than 1')
    
        options['_filter'].limit = options['limit']
        
@option(convert = float)
def sample(options):
    ''' The sample option generates a subset dataset from the original dataset. 
    When saving or loading each row there is *x*% chance that the row will be saved or loaded 
    such that *x* = *options['sample']* with 0 < *options['sample']* <= 1. 
    OptionError raised if 0 >= *options['sample']* > 1.  
    
    >>> import cardsharp as cs
    >>> from cardsharp.test import get_temp_file
    >>> ds = cs.Dataset(['a', 'b', 'c'])
    >>> ds.wait()
    >>> for x in range(100):
    ...     ds.add_row([unicode(x), unicode(x), unicode(x)])
    >>> with get_temp_file('txt') as temp:
    ...     ds.save(source = temp.name, format = 'text', sample = 1.0, encoding = 'utf-8')
    ...     ds.wait()
    ...     d1 = cs.load(source = temp.name, format = 'text', encoding = 'utf-8')
    ...     d1.wait()
    ...     assert len(d1.rows) == 100
    ...     ds.save(source = temp.name, format = 'text', sample = 0.5, encoding = 'utf-8', overwrite=True) 
    ...     ds.wait()
    ...     d1 = cs.load(source = temp.name, format = 'text', encoding = 'utf-8')
    ...     d1.wait()
    ...     assert 40 < len(d1.rows) < 60
    ...     ds.save(source = temp.name, format = 'text', sample = 0.0000001, encoding = 'utf-8', overwrite = True) 
    ...     ds.wait()
    ...     d1 = cs.load(source = temp.name, format = 'text', encoding = 'utf-8')
    ...     d1.wait()
    ...     assert len(d1.rows) == 0
    '''
    if 'sample' in options:
        if 0 < options['sample'] <= 1:
            options['_filter'].sample = options['sample']
        else:
            raise OptionError('Sample must be between 0 and 1')
    
@option(convert = int)
def skip(options):
    ''' Skips *x* number of rows when saving or loading where *x* is the value of *options['skip']*. 
    OptionError raised if *options['skip']* < 0. 
    
    >>> import cardsharp as cs
    >>> from cardsharp.test import get_temp_file
    >>> ds = cs.Dataset(['a', 'b', 'c'])
    >>> ds.wait()
    >>> for x in range(100):
    ...     ds.add_row([unicode(x), unicode(x), unicode(x)])
    >>> with get_temp_file('txt') as temp:
    ...     ds.save(source = temp.name, format='text', skip='90', encoding='utf-8')
    ...     ds.wait()
    ...     d1 = cs.load(source = temp.name, format='text', encoding='utf-8')
    ...     d1.wait()
    ...     assert len(d1.rows) == 10
    ...     for x in d1:
    ...         x
    Row([u'9', u'9', u'9'])
    Row([u'8', u'8', u'8'])
    Row([u'7', u'7', u'7'])
    Row([u'6', u'6', u'6'])
    Row([u'5', u'5', u'5'])
    Row([u'4', u'4', u'4'])
    Row([u'3', u'3', u'3'])
    Row([u'2', u'2', u'2'])
    Row([u'1', u'1', u'1'])
    Row([u'0', u'0', u'0'])
    '''
    if 'skip' in options:
        if options['skip'] < 0:
            raise OptionError('Skip cannot be less than zero')
    
        options['_filter'].skip = options['skip']

@option(stage = VARIABLES_STAGE)
def keep(options):
    keep_vars = options.get('keep')
    if keep_vars:
        vars = options['_variables']
        vars._keep[:] = [False] * len(vars._keep)
        for var in keep_vars:
            vars._keep[vars.index(var)] = True

@after('keep')
@option(stage = VARIABLES_STAGE)
def drop(options):
    drop_vars = options.get('drop')
    if drop_vars:
        if 'keep' in options:
            raise OptionError('Cannot specify both keep and drop variables')
        
        vars = options['_variables']
        for var in drop_vars:
            vars._keep[vars.index(var)] = False
            
@option(required=False)
def cache_type(options):
    """Set the format the value should be stored in the cache. Either as a dict or a list.
    If cach_type = 'dict' the value for a given cach_key will be a dict mapping var.name to var.value 
    for each var in the dataset which is not listed in the cache_key. 
     
    If cach_type = 'list' the value for a given cach_key will be a list of  
    each var in the dataset which is not listed in the cache_key.
    """
    if options.get('cache_type') and (not instance(options.get('cache_type'), dict) or not isinstance(options.get('cache_type'), list)):
        raise OptionError('cache_type can only be a list or dict. ')
 
@option(required=False)
def cache_key(options):
    if options.get('cache_key'):
        if not isinstance(options['cache_key'], list):
            raise OptionError('cache_key option must be a list of variable names')
        for v_name in options.get('cache_key'):
            if v_name not in options.get('_variables'):
                raise OptionError('cache key variable name: %s is not valid.' % v_name)
    
    
@option(required=False)
@after('cache_key')
def as_cache(options):
    if 'cache_key' is None:
        raise OptionError('Must specify a cache_key option.')

@option(required=False)
def memcache(options):
    pass
    
# @_o('rename', valid = 'load', vars = True)
# def _opt(options):
#    internal_names = _rename(options.get('rename'), options.external_names)
#    options.variables = VariableBundle(vd.create_variable(n) for n, vd in izip(internal_names, options.var_defs))
# 

@option(default = lambda r: True)
def filter(options):
    pass

def _rename(renamer, variables):
    """Renames a list of variables according to the option provided.

    >>> vars = ['Var A', 'Var B', 'Var C', 'Var D', 'Var E']
    >>> _rename(None, vars)
    [u'Var A', u'Var B', u'Var C', u'Var D', u'Var E']
    >>> import re
    >>> _rename((re.compile(r'Var\\s*([A-E])'), r'\\1 replaced'), vars)
    [u'A replaced', u'B replaced', u'C replaced', u'D replaced', u'E replaced']
    >>> _rename(unicode.lower, vars)
    [u'var a', u'var b', u'var c', u'var d', u'var e']
    >>> _rename({ 'Var A' : 'Other A', 'Var D' : 'Other D' }, vars)
    [u'Other A', u'Var B', u'Var C', u'Other D', u'Var E']
    >>> _rename(['A', 'B', 'C'], vars)
    [u'A', u'B', u'C', u'Var D', u'Var E']
    >>> _rename(12, vars)
    Traceback (most recent call last):
        ...
    OptionError: Invalid argument for rename: 12
    """

    if renamer is None:
        return list(variables)

    if hasattr(renamer, '__call__'):
        return [(renamer(s) or s) for s in variables]

    try:
        if isinstance(renamer, Sequence) and len(renamer) == 2 and isinstance(renamer[0], re._pattern_type):
            pattern, repl = renamer
            return [pattern.sub(repl, s) for s in variables]
        
        try:
            return [(renamer.get(s) or s) for s in variables]
        except:
            return list(r or v for r, v in izip_longest(renamer, variables))[:len(variables)]

    except:
        raise OptionError('Invalid argument for rename: %r' % renamer)

def _fix_cardsharp_path(source):
    return os.path.normcase(os.path.abspath(os.path.join(cardsharp.settings.data_dir, source)))
