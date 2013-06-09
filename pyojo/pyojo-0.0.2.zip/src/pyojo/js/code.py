# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Base classes and functions for javascript generation.
"""
from pyojo.func import Error, raw_str



def js_dict(obj, var=False):
    """ Generate Javascript representation for a dictionary.
        
        :param obj: dictionary
        :param var: if True, do not quote the keys 
        
        :returns: str
    """
    x = ""
    for key, val in obj.iteritems():
        if type(key) == type(""):
            if var:
                x += "%s: %s, " % (key, js_code(val))
            else:
                x += "'%s': %s, " % (key, js_code(val))
        else:    
            x += "%s: %s, " % (js_code(key), js_code(val))
    return "{"+x[:-2]+"}"


# JavaScript conversion functions
__JS_REPR={type(""):   lambda v: "'"+v+"'",
           type(u""):  lambda v: u"'"+v+u"'",
           type(0):    lambda v: str(v),
           type(0.0):  lambda v: str(v),
           type(True): lambda v: 'true' if v else 'false',
           type(None): lambda v: 'null',
           type([]):   lambda v: "["+", ".join(map(js_code, v))+"]",
           type({}):   js_dict}


def js_code(obj):
    """ Returns javascript code from a python object.
    
        This function does not return any require block.
    
        :param obj: any object
        :returns: Javascript Code
        :rtype: string
    """
    
    convert = __JS_REPR.get(type(obj))
    if convert is not None: 
        return convert(obj)
    
    if isinstance(obj, (Code, Object)): 
        return obj.code()
    
    if isinstance(obj, dict):
        return js_dict(obj)

    raise JavascriptError("Unable to convert %s" % type(obj))



def js_try(code, obj=None):
    """ Create a try-catch statement and log errors.
        
        :param code: string
        :param obj: string or any object      
    """
    if obj is None: block="?"
    elif type(obj)==type(""): block=obj
    else: 
        block = obj.__class__.__name__
        if hasattr(obj, "name"): 
            if obj.name is not None:
                block = obj.name+"="+block        
    
    msg = raw_str("javascript block [%s]\\n\\n" % block)
    return "try {%s} catch(err){alert('%s'+err)}" % (code, msg)



def js_check(var, code):
    """ Executes the code only if var is undefined.
    """
    return "if (typeof %s == 'undefined') {%s}" % (var, code)


def has_require(codes):
    """ Checks if any of the blocks has Dojo requires.
    """
    check = []
    for code in codes:
        if getattr(code, "require", None) is not None:
            return True
        if isinstance(code, Var):
            if code.value is not None: 
                check.append(code.value) 
        else:
            check += getattr(code, "blocks", [])
    return any(getattr(_, "require", None) is not None for _ in check)



#----------------------------------------------------------------------------
#--- Classes


class Object(dict):

    def code(self):
        """ Get the JavaScript constructor code.
        """
        param = js_dict(self, True) if len(self.keys())>0 else ""
        if self.__class__.__name__ == "Object" and param != "":
            return param
        else:
            return "new %s(%s)" % (self.__class__.__name__, param)
                        



class Code(object):
    """ A javascript code block.
    
        When you want to pass a parameter name, this allows to know that it 
        should not have any quotes.
    
        Attributes:
         
         - **catch**: Put this code inside a try-catch JavaScript block.
         
        Example::
        
            >>> a = Code("alert('A');")
            >>> b = Code("alert('B');")
            >>> a
            alert('A');
            >>> a+b
            alert('A');
            alert('B');
        
        .. note:: str will return compressed js
    """
    
    loc = ""
    """ Contains the javascript code:
    
        .. code::
        
              >>> script = Code("alert('1');")
              >>> str(script) 
              "alert('1');"
              >>> script.js 
              "alert('1');"
    """
    
    catch = False

    def __init__(self, loc=None):
        """ Create a code block.
            
            :param loc: The javascript code.
            :type loc: string
        """
        if loc is not None: self.loc = loc
    
    def script(self, loc):
        """ Add code.

            :param loc: The javascript code.
            :type loc: string
        """
        self.loc += loc
        return self 
    
    def code(self):
        """ Return the JavaScript code.
        
            :returns: string
        """
        if self.catch:
            return js_try(self.loc, self)
        else:
            return self.loc    
    
    def add_loc(self, loc):
        self.loc += loc
        return Code(loc) 
        
    def __str__(self):
        """ The string conversion of a Code object is expected to return the 
        source code.
        """
        return self.code()

    def __repr__(self):
        cls = self.__class__.__name__
        if cls=="Code": 
            return "<Code '%s'>" % (self.loc)
        else: 
            return "<Code %s '%s'>" % (cls, self.loc)

    def __add__(self, other):
        """ Code blocks can be added::
        
            JS = menu + document + events
        """
        if hasattr(other, "loc"):
            self.loc = self.loc + "\n" + other.loc
        else:
            self.loc += "%s" % other
        #require = self.require + other.require
        return Code(self.loc)
        


class Var(Code):
    """ Represents a javascript variable.
    """
    def __init__(self, var, value=None, local=True):
        """ Declare a Javacript variable.
        """
        if type(var)!=type(""):
            raise JavascriptError("Variable name must be a string")
        self.var = Code(var)
        self.value = value
        self.local = local
        
        
    def __str__(self):
        return self.var.loc

    def get_requires(self):
        if self.value is None: 
            return []
        if getattr(self.value, "get_requires", None) is None: 
            return []
        return self.value.get_requires() 
    
    def code(self):
        if self.value is None:
            return self.var.loc
        var = "var " if self.local else ""
        val = " = %s" % js_code(self.value)
        code = var + self.var.loc + val
        if not code.endswith(";"): 
            code += ";"
        return code



class Function(Code):
    """ Declares a javascript function.
    """
    def __init__(self, *args):
        """ The last argument is the function code, or a list.
        """
        if len(args)>0:
            self.param = args[0:-1]
            blocks = args[-1]
            if isinstance(blocks, list):
                self.blocks = blocks
            else:
                self.blocks = [blocks]
        else:
            self.param = []
            self.blocks = []
        
    def get_requires(self):
        """ Returns a list with all the requires found.
        """
        requires = []
        
        for block in self.blocks:
            get_requires = getattr(block, "get_requires", None)
            if get_requires is not None:
                requires += get_requires()
        return requires
        
    def __add__(self, block):
        self.blocks.append(block)
        return self
        
        
    def code(self):
        func = ""
        for block in self.blocks:
            if isinstance(block, basestring):
                func += block
            else:
                func += js_code(block)
            
        self.loc = "function(%s) {%s}" % (", ".join(self.param), func)
        return super(Function, self).code()


#----------------------------------------------------------------------------
#--- Errors


class JavascriptError(Error):
    """ Base class for specific pyojo known errors.
    """
    def __init__(self, value):
            self.value = value
    def __str__(self):
        return repr(self.value)
    
