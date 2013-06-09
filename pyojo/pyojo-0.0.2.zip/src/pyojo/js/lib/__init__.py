# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Javascript code block generation functions.

This functions are dinamically generated from tamplates at import time.
"""

import os
import re
import sys

def __generate_functions():
    """ Generates a collection of functions from the templates.
    """
    def define_function(name, code):
        """ Generate one function from template.
        """
        var = []
        for variable in re.findall(r'__(\w*)__', code):
            if not variable in var: 
                var.append(variable)
        doc = []
        line = []
        for ln in code.split('\n'):
            if ln == '\n': 
                continue
            if ln.startswith("//"): 
                doc.append(ln[2:])
            else: 
                line.append(ln)
       
        doc = '\n       '.join(doc).strip('\n')
        code = '\n'.join(line).strip('\n')
        for variable in var:
            doc = doc.replace('__'+variable+'__', variable)
        
        src = "\n\n:rtype: string"
        src += "\n:returns: JavaScript code\n\n"
        src += "    .. code-block:: javascript\n"
        src += '\n          '+'\n          '.join(code.split('\n'))
        
        doc += '\n        '.join(src.split('\n'))
        args = {}
        for arg in var:
            args[arg] = "z"
        
        para = str(var).replace("'","")[1:-1]
        fcode = "def %s(%s):\n" % (name, para)
        fcode += '    """%s\n' % doc
        fcode += '    """\n'
        fcode += "    tmpl='''%s'''\n" % code
        #f+= "    for arg in [%s]:\n" % para
        #f+= "        tmpl = tmpl.replace('__'+arg+'__', str(arg))\n" 
        for v in var:
            fcode += "    tmpl = tmpl.replace('__%s__', str(%s))\n" % (v, v) 
        fcode += "    return tmpl\n" 
        fcode += ""
        return fcode
    
    path = os.path.join(os.path.dirname(__file__), "js")
    for filename in os.listdir(path):
        name, ext = os.path.splitext(filename)
        if ext != ".js": 
            continue
        with open(os.path.join(path, filename)) as tmpl:
            yield define_function(name, tmpl.read())
    
   
for _source in __generate_functions():
    exec compile(_source, '<string>', 'exec')


#del source

#print dir(sys.modules[globals()['__name__']])

#import inspect
#lines, x = inspect.getsourcelines(alert)
#for x in lines:
#    print "%s" % (x),

    
# ----------------------------------------------------------------------------
