# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------


import time
import unittest
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import pyojo
from pyojo import js, jsbeautify, raw_str
from pyojo.js import dojo



def _no_console():
    #log = r"log = function(text) {x = document.getElementById('base'); x.innerHTML+= text + '\n';}"
    log = r"log = console.log;"
    
    return log

def _create_console():
    textarea = dojo.domConstruct.create("textarea", "base", id="log")
    log = r"log = function(text) {text_log.innerHTML+= text + '\n';}"
    return js.get_code(js.Var("text_log", textarea, False), log)


class pyojoTest(unittest.TestCase):
    console = True
    
    def url(self, url="/test.html"):
        self.browser.get(self.base_url + url)

    def log(self, msg=""):
        self.browser.execute_script("log('%s');" % raw_str(msg))


    def script(self, script):
        self.browser.execute_script(script)
        
    def js(self, script="", title="Script"):
        self.log("%s:" % title)
        self.log(jsbeautify(script))
        try:
            result = self.browser.execute_script(script)
            
            self.log("OK%s" % ("" if result is None else ": %s" % result))
            self.log()
            #time.sleep(1)
            
        except WebDriverException, e:
            self.log("ERROR: %s" % e.msg)
            time.sleep(5)
            print jsbeautify(script)
            raise
        return result

    def code(self, *blocks):
        self.log("Testing %s" % repr(blocks))
        self.js(js.get_code(*blocks))
        
    def find_id(self, name):
        elem = self.browser.find_element_by_id(name)
        self.log("Found id='%s'" % name)
        return elem
        
    def elem_keys(self, elem, keys):        
        elem.send_keys(keys)
        elem.send_keys(Keys.RETURN)        

    def setUp(self):
        self.base_url = "http://127.0.0.1"
        self.browser = webdriver.Firefox()
        self.browser.get("http://127.0.0.1/test.html")

        if self.console:
            self.browser.execute_script(_create_console())
        else:
            self.browser.execute_script(_no_console())

        msg = "Test "+ self.id()
        self.log(msg)
        self.log("-"*len(msg))
        desc = self.shortDescription()
        if desc is not None:
            self.log(desc)
        self.log()
        

    def tearDown(self):
        msg = "Completed "+ self.__class__.__name__
        self.log()
        self.log(msg)
        time.sleep(1)
        #self.browser.close()
        self.browser.quit()


    def checkIf(self, script, expected=True):
        result = self.js("return %s;" % script, "Checking")
        self.assertEqual(result, expected, 
                         "CheckIf (%s)=%s, not %s" % (script, 
                                                      result, 
                                                      expected))
        
class Automated_Title(pyojoTest):
    """ The pyojo selenium tests.  
    
    Welcome to the automated browser test suite
    -------------------------------------------
    
    Now we are going to launch many browser windows, please wait.
    
    Let's begin ...
    """
    def test_console(self):
        self.script("log('pyojo version %s');" % pyojo.__version__)
        self.script("log('Dojo version '+dojo.version);")
        
        self.assertIn("pyojo", self.browser.title)
        elem = self.browser.find_element_by_id("log")
        for line in "Please wait ...".split("\n"):
            self.elem_keys(elem, line)
        time.sleep(1)



if __name__ == "__main__":
    unittest.main()
