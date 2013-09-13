#-*- coding: utf-8 -*-
from pyramid_rest.helpers import bcolors
import json
import requests as r
import unittest
from sqlalchemy.engine.base import Transaction
import transaction
import sqlahelper

class Test:
    COOKIES = {}
    URL_PREFIX = ""
    
    @staticmethod
    def set_url_prefix(url):
        Test.URL_PREFIX = url
    
    @staticmethod
    def set_cookies(dict):
        Test.COOKIES = dict
    
    @staticmethod
    def clear_cookies():
        Test.COOKIES = {}
        
    def __init__(self, name=""):
        print bcolors.OKBLUE, "\n\n----------------------- At testing %s-----------------------\n"%name, bcolors.ENDC
    
    def _kindAssertEqual(self, left, right, name=""):
        try:
            assert left == right
        except AssertionError:
            if not hasattr(self, "json"):
                self.parse()
            
            print bcolors.FAIL, "Error. %s: AssertionError. Expected %s, gets %s. Metadata: \n\tJSON response: %s"%(name, right, left, getattr(self, "json", "No json data")), bcolors.ENDC
            if not hasattr(self, "json"):
                with open("test.html", "w") as fd:
                    fd.write(self.response.text)
            raise AssertionError
    
    def post(self, url, **k):
        if not "cookies" in k:
            k["cookies"] = self.COOKIES
        url = self.URL_PREFIX + url
        if "data" in k:
            k["data"] = json.dumps(k["data"])
        self.response = r.post(url, **k)
        self.text = self.response.text
        return self
    
    def get(self, url, **k):
        if not "cookies" in k:
            k["cookies"] = self.COOKIES
        url = self.URL_PREFIX + url
        if "data" in k:
            k["data"] = {"query": json.dumps(k["data"])}
        self.response = r.get(url, **k)
        self.text = self.response.text
        return self
    
        if not hasattr(self, "json"):
            self.parse()
    def put(self, url, **k):
        if not "cookies" in k:
            k["cookies"] = self.COOKIES
        url = self.URL_PREFIX + url
        if "data" in k:
            k["data"] = json.dumps(k["data"])
        self.response = r.put(url, **k)
        self.text = self.response.text
        return self
    
    def delete(self, url, **k):
        if not "cookies" in k:
            k["cookies"] = self.COOKIES
        url = self.URL_PREFIX + url
        if "data" in k:
            k["data"] = json.dumps(k["data"])
        self.response = r.delete(url, **k)
        self.text = self.response.text
        return self
    
    def parse(self):
        try:
            self.json = self.response.json()
        except:
            print bcolors.FAIL, "Error, no JSON data found. Response: \n%s"%self.response.text, bcolors.ENDC
            with open("test.html", "w") as fd:
                fd.write(self.response.text)
            raise AssertionError
        return self
        
    def assertCode(self, code):
        self._kindAssertEqual(self.response.status_code, code, "assertCode")
        return self
    
    def assertEqual(self, names, value, name="assertEqual"):
        if not hasattr(self, "json"):
            self.parse()
        
        if hasattr(names, "__iter__"):
            gettedVal = self.json
            
            for name in names:
                gettedVal = gettedVal[name]
        else:
            gettedVal = self.json[names]
        
        self._kindAssertEqual(gettedVal, value)
        return self
    
    def assertJson(self, value):
        if not hasattr(self, "json"):
            self.parse()
        
        self._kindAssertEqual(self.json, value)
        
    
    def log(self):
        if not hasattr(self, "json"):
            self.parse()
        print bcolors.OKGREEN, "Response metainfo:\n\t%s"%repr(self.json).decode("unicode-escape"), bcolors.ENDC
        return self

class Case(unittest.TestCase):
    def setUp(self):
        print bcolors.OKBLUE, "clearing tables", bcolors.ENDC
        print bcolors.OKBLUE, "inserting data tables", bcolors.ENDC
        with transaction.manager:
            for table in reversed(self.Base.metadata.sorted_tables): 
                table.delete().execute()
                transaction.commit()
        
        #self.base.metadata.create_all(self.engine)
        print bcolors.OKBLUE, "ok"
        
    def tearDown(self):
        Test.clear_cookies()
        return
        with transaction.manager:
            for table in reversed(self.Base.metadata.sorted_tables): 
                self.DBSession.execute(table.delete())
                transaction.commit()
        print bcolors.OKBLUE, "ok", bcolors.ENDC
    
    def __init__(self, *a, **k):
        unittest.TestCase.__init__(self, *a, **k)
        
        self.Base = sqlahelper.get_base()
        self.DBSession = sqlahelper.get_session()
        self.engine = sqlahelper.get_engine()