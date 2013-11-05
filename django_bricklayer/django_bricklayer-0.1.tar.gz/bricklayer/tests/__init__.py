from bricklayer.tests.generatecrud import *  
from bricklayer.tests.generatecommand import * 
from bricklayer.tests.generateadmin import * 
from bricklayer.tests.generateform import * 
from bricklayer.tests.testpackage import * 
from bricklayer.tests.addtest import * 
#starts the test suite  
__test__= {  
           'generatecrud': [generatecrud],
           'generatecommand': [generatecommand],
           'generateadmin': [generateadmin],
           'generateform': [generateform],
           'addtest': [addtest],
           'testpackage':[testpackage]
           }  