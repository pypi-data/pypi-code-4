#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Search for (similar) web pages

#Imports
import sqlite as sql
# import sqlite3 as sql #Problem with sql.connect()
import os
import time

__author__ = "Jorge Blanco"
__description__ = "Create, search and analyze a DB with your Apple's newsstand app information"
__email__ = "mail [at] jorgeblan [dot] co"
__license__ = "GPLv2"
__maintainer__ = "Jorge Blanco"
__status__ = "Development"
__version__ = "0.2"

class newsstandDB:
    '''
    Create, search and analyze a DB with Apple's newsstand information
    **********************************
    Usage:
        createDB('filename') #Creates the DB
        importData('filename') #imports CSV file into the data table
        importOptin('filename') #imports the optin file into the optin table
        buildStats() #Analyzes the data and updates the stats table
    '''
    __path = os.path.split(__file__)[0]
    __log = True
    __logfile = os.path.join(__path, 'newsstandDB.log')
    __dataStructure = (('Provider','TEXT'),('Provider Country','TEXT'),('SKU','TEXT'),
                       ('Developer','TEXT'),('Title','TEXT'),('Version','TEXT'),
                       ('Product Type Identifier','TEXT'),('Units','INTEGER'),
                       ('Developer Proceeds','REAL'),('Customer Currency','TEXT'),
                       ('Country Code','TEXT'),('Currency of Proceeds','TEXT'),
                       ('Apple Identifier','TEXT'),('Customer Price','REAL'),
                       ('Promo Code','TEXT'),('Parent Identifier','TEXT'),
                       ('Subscription','TEXT'),('Period','TEXT'),('Download Date (PST)','TEXT'),
                       (' Customer Identifier','TEXT'),('Report Date (Local)','TEXT'),
                       ('Sales/Return','TEXT'),('Category','TEXT'))
    
    def __init__(self, dbpath):
        '''init: Connect to the database and initialize variables'''
        #Connect to the database
        assert dbpath
        self.conn = sql.connect(dbpath)
        self.cur = self.conn.cursor()
        print 'Connected to the database'
        
    def __del__(self):
        '''del: Try to shutdown as cleanly as possible. Close the database connection and open file handles'''
        self.conn.close()
    
    def log(self,msg):
        '''log(msg): Write msg to the log'''
        if self.__log:
            try:
                with open(self.__logfile,'a') as fp:
                    fp.write(time.asctime()+': '+msg+'\n')
            except IOError:
                print 'Unable to write to logfile %s' % self.__logfile
    
    def setLog(self,log,logfile=None):
        '''setLog(log): Set the logging on or off. (Optional) Change the logfile'''
        if log:
            self.__log = True
        else:
            self.__log = False
        if logfile:
            self.__logfile = logfile
            
    def uniqueList(self, seq):
        '''uniqueList(seq): return a list containing only one instance of each element in seq'''
        seen = set()
        return [ x for x in seq if x not in seen and not seen.add(x)]