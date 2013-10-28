#Imports
# import sqlite as sql
import sqlite3 as sql #Problem with sql.connect()
import os
import time
import csv
from hashlib import md5
from dateutil.relativedelta import relativedelta
from datetime import datetime
from os.path import isfile
from os.path import abspath
from csvreader import unicode_csv_reader as ucsvreader
# from __future__ import division

__author__ = "Jorge Blanco"
__description__ = "Create, search and analyze a DB with your Apple's newsstand app information"
__email__ = "py [at] jorgeblan [dot] co"
__license__ = "GPLv2"
__maintainer__ = "Jorge Blanco"
__status__ = "Development"
__version__ = "0.1"

class newsstandDB:
    '''
    Create, search and analyze a DB with Apple's newsstand information
    **********************************
    Usage:
        createDB() #Creates the DB tables (DB file itself is created at __init__)
        removeDB() # Deletes the DB file
        importCSV(filename) #imports CSV file into a buffer
        importData(filename) #imports CSV file into the data table
        importOptin(filename) #imports the optin file into the optin table
        multiImport(*files) #Import files into DB
        buildStats() #Analyzes the data
        writeStats() #Writes the stats into the stats table
        outputStats(filename) #Write current stats to external file
        log(msg) #Write msg to the log
        setLog(log,logfile=None) #Set the logging on or off. (Optional) Change the logfile
        uniqueList(seq) #return a list containing only one instance of each element in seq
        md5Checksum(filename, block_size=2**20) #return the MD5 hash of t
        fileInDB(filename) #Check that the file has not been read yet
        calculateUniqueUsers() #calculate the amount of people who downloaded the app (unique)
        calculatePayingUsers() #calculate the amount of people who made a purchase
        calculateConversion(users,payingUsers) #calculate the ratio between people who 
            download the app and people who make a purchase
        calculateProceeds(product) #Calculate the proceeds depending on the Product Type 
            Identifier
        calculateTotalProceeds() #calculate the total revenue
        calculateProceedsPerUser(proceeds,users) #calclulate the ratio between proceeds 
            and total downloads (unique)
        calculateCLV(proceeds,payingUsers) #calculate the customer lifetime value 
            (ratio between total paying usrs and proceeds)
        calculateCurrentSubscribers() #calculate the amount of subscribers active in 
            the past 30 days
        addProduct(cutoffDdate,product,price) #Add a product to the product table
        getProductProceeds(date,product) #get the price of a product at a certain date
        
    '''
    __path = os.path.split(__file__)[0]
    __log = True
    __logfile = os.path.join(__path, 'newsstandDB.log') #TODO: Add logging to functions
    __dataStructure = ('Provider TEXT','ProviderCountry TEXT','SKU TEXT',
                       'Developer TEXT','Title TEXT','Version TEXT',
                       'ProductTypeIdentifier TEXT','Units INTEGER',
                       'DeveloperProceeds REAL','CustomerCurrency TEXT',
                       'CountryCode TEXT','CurrencyOfProceeds TEXT',
                       'AppleIdentifier TEXT','CustomerPrice REAL',
                       'PromoCode TEXT','ParentIdentifier TEXT',
                       'Subscription TEXT','Period TEXT','DownloadDatePST TEXT',
                       'CustomerIdentifier TEXT','ReportDate_Local TEXT',
                       'SalesReturn TEXT','Category TEXT DEFAULT \'\'')
    __fileStructure = ('filename TEXT UNIQUE','hash TEXT UNIQUE')
    __statsStructure = ('Date TEXT','UniqueUsers INTEGER','PayingUsers INTEGER',
                        'Conversion REAL','TotalProceeds REAL','ProceedsPerUser REAL',
                        'CLV REAL','CurrentSubscribers INTEGER')
    __monthProceedsStructure = ('Month TEXT','Proceeds REAL')
    __optinStructure = ('FirstName TEXT','LastName TEXT','EmailAddress TEXT',
                        'PostalCode TEXT','AppleIdentifier TEXT',
                        'ReportStartDate TEXT','ReportEndDate TEXT')
    __productStructure = ('CutoffDate TEXT','Product TEXT','Proceeds REAL')
    
    __dbFilename = ''
    __pDBFile = os.path.join(__path, 'dbfile') #Persistent DB file store
    
    __uniqueUsers = 0
    __payingUsers = 0
    __conversion = 0
    __totalProceeds = 0
    __proceedsPerUser = 0
    __clv = 0
    __currentSubscribers = 0
    
    __dateFormat = '%m/%d/%Y'
    
    def __init__(self, dbPath='newsstandDB.sql',atBase=False):
        '''init: Connect to the database and initialize variables'''
        #Connect to the database
        if dbPath == ':memory:':
            self.__dbFilename = ':memory:'
        else:
            if not atBase:
                realFilename = abspath(dbPath)
            else:
                realFilename = os.path.join(self.__path, dbPath)
            self.__dbFilename = realFilename
#         assert self.__dbFilename #Unnecessary?

        try:
            self.con = sql.connect(self.__dbFilename)
        except sql.OperationalError: #If unable to connect to the database
            print '\nError: Unable to connect to the database (Err13)\n'
            exit(-1)
        else:
            self.cur = self.con.cursor()
            print 'Connected to the database\n'
        
    def __del__(self):
        '''del: Try to shutdown as cleanly as possible. Close the database connection and open file handles'''
        try:
            self.con.close()
        except AttributeError:
            print '\nError: No connection to close (Err5)\n'
    
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
            
#     def uniqueList(self, seq):
#         '''uniqueList(seq): return a list containing only one instance of each element in seq'''
#         seen = set()
#         return [ x for x in seq if x not in seen and not seen.add(x)]
    
    def md5Checksum(self,filename, block_size=2**20):
        '''md5Checksum(filename, block_size=2**20): return the MD5 hash of filename'''
        md5sum = md5()
        with open (filename, "r") as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                md5sum.update(data)
        return md5sum.hexdigest()
    
    def calculateUniqueUsers(self):
        '''calculateUniqueUsers(): calculate the amount of people who downloaded the app (unique)'''
        self.cur.execute('SELECT DISTINCT CustomerIdentifier FROM data')
        return len(self.cur.fetchall())
    
    def calculatePayingUsers(self):
        '''calculatePayingUsers(): calculate the amount of people who made a purchase'''
        self.cur.execute('SELECT CustomerIdentifier FROM data WHERE CustomerPrice > 0')
        return len(set(self.cur.fetchall()))
    
    def calculateConversion(self,users,payingUsers):
        '''calculateConversion(users,payingUsers): calculate the ratio between people who 
        download the app and people who make a purchase'''
        try:
            return payingUsers/float(users)
        except ZeroDivisionError:
            return 0.0
    
    def calculateProceeds(self,product,date):
        '''calculateProceeds(product): Calculate the proceeds depending on the Product Type 
        Identifier'''
        #TODO: Eliminate this function (redundant)
        try:
            return self.getProductProceeds(date, product)
        except:
            raise
#         if product=="IA1":
#             return 3.5
#         elif product=="IAY":
#             return 2.1
#         else:
#             raise #TODO: Define exception
    
    def calculateTotalProceeds(self):
        '''calculateTotalProceeds(): calculate the total revenue'''
        self.cur.execute("SELECT ProductTypeIdentifier,DownloadDatePST FROM data WHERE CustomerPrice > 0")
        proceedsList = [self.calculateProceeds(product[0],product[1]) for product in self.cur.fetchall()]
        self.cur.execute("SELECT ProductTypeIdentifier,DownloadDatePST FROM data WHERE CustomerPrice < 0")
        proceedsList += [self.calculateProceeds(product[0],product[1])*-1.0 for product in self.cur.fetchall()]
        return sum(proceedsList)
    
    def calculateProceedsPerUser(self,proceeds,users):
        '''calculateProceedsPerUser(proceeds,users): calclulate the ratio between proceeds 
        and total downloads (unique)'''
        try:
            return proceeds/float(users)
        except ZeroDivisionError:
            return 0.0
    
    def calculateCLV(self,proceeds,payingUsers):
        '''calculateCLV(proceeds,payingUsers): calculate the customer lifetime value 
        (ratio between total paying usrs and proceeds)'''
        try:
            return proceeds/float(payingUsers)
        except ZeroDivisionError:
            return 0.0
    
    def calculateCurrentSubscribers(self):
        '''calculateCurrentSubscribers(): calculate the amount of subscribers active in 
        the past 30 days'''
        
        self.cur.execute('''SELECT DownloadDatePST FROM data WHERE Subscription 
                         IN ('New','Renewal') AND SalesReturn='S';''')
        data = self.cur.fetchall()
        try:
            maxDate = max(data)[0]
        except ValueError:
            print 'Empty sequence for current subscribers'
            return 0
#         print maxDate #Debug
        maxDatetime = datetime.strptime(maxDate, self.__dateFormat).date()
        datetimeLimit = maxDatetime - relativedelta(months=1)
        dateLimit = datetime.strftime(datetimeLimit, self.__dateFormat)
        
        filteredData = [date[0] for date in data if date[0]>dateLimit ]
        
#         print filteredData #Debug
#         print len(filteredData) #Debug
        return len(filteredData)
    
    def createDB(self): 
        '''createDB(): Creates the DB tables (DB file itself is created at __init__)'''
        try:
            for name,structure in [('data',self.__dataStructure),('file',self.__fileStructure),
                                   ('stats',self.__statsStructure),
                                   ('monthProceeds',self.__monthProceedsStructure),
                                   ('optin',self.__optinStructure),
                                   ('product',self.__productStructure)]:
                try:
                    code = ''.join(["CREATE TABLE ",name," (",', '.join(structure),")"])
                    with self.con:
                        self.con.execute(code)
                except sql.OperationalError:
                    pass
        except:
            raise
        else:
            try:
                if self.__dbFilename != ':memory:':
                    self.setDBFile(self.__dbFilename)
            except IOError:
                print 'Could not set persistent DB file'
        
    
    def removeDB(self): 
        '''removeDB(): Deletes the DB file'''
        try:
            os.remove(self.__dbFilename)
        except IOError:
            print 'Could not remove database'
            raise
    
    def importCSV(self,filename,skipHeader=True): 
        '''importCSV(filename): imports CSV file into a buffer'''
        if not isfile(filename):
            raise IOError
        with open(filename,'r') as fin:
            readerData = ucsvreader(fin, delimiter='\t')
#             readerData = csv.reader(fin, delimiter='\t') #old csv reader (doesnt support utf8)
            if not skipHeader:
                return [[j for j in i] for i in readerData]
            else:
                return [[j for j in i] for i in readerData][1:]
            
    def insertFileToDB(self,filename):
        '''insertFileToDB(filename): Insert filename into DB to keep records unique'''
        with self.con:
            self.con.execute("INSERT INTO file VALUES (?,?)",(filename,self.md5Checksum(filename)))
        
    def fileInDB(self,filename):
        '''fileInDB(filename): Check that the file has not been read yet'''
        self.cur.execute("SELECT filename FROM file WHERE filename=?",(filename,))
        if len(self.cur.fetchall()) > 0:
            raise sql.IntegrityError
        else:
            return True
        
    
    def importData(self,filename): 
        '''importData(filename): imports CSV file into the data table'''
        try:
            self.fileInDB(filename)
        except:
            return False #Skip silently
#             raise #Debug
        else:
            try:
                data = self.importCSV(filename)
            except csv.Error:
                print "Could not parse file (Err45)"
                raise
            try:
                with self.con:
                    self.con.executemany(''.join(['INSERT INTO data VALUES (',
                                              ','.join(['?']*len(self.__dataStructure)),')']), 
                                     data)
            except:
                try:
                    with self.con:
                        data2 = [x + [u''] for x in data]
#                         print data2 #Debug
                        self.con.executemany(''.join(['INSERT INTO data VALUES (',
                                                  ','.join(['?']*len(self.__dataStructure)),')']), 
                                         data2)
                except:
                    raise
            self.insertFileToDB(filename)
    
    def importOptin(self,filename): 
        '''importOptin(filename): imports the optin file into the optin table'''
        try:
            self.fileInDB(filename)
        except:
            return False #Skip silently
#             raise #Debug
        else:
            try:
                data = self.importCSV(filename)
            except csv.Error:
                print "Could not parse file (Err45)"
                raise
            with self.con:
                try:
                    data2 = [x[:-1] for x in data]
                    self.con.executemany(''.join(['INSERT INTO optin VALUES (',
                                                 ','.join(['?']*len(self.__optinStructure)),
                                                 ')']), data2)
                except:
#                     raise #No need for the code below in reaal life, as the files always
#                            include the extra empty field
                    try:
                        self.con.executemany(''.join(['INSERT INTO optin VALUES (',
                                                 ','.join(['?']*len(self.__optinStructure)),')']), 
                                         data)
                    except:
                        print data
                        raise
            self.insertFileToDB(filename)
            
    def multiImport(self,*files):
        '''multiImport(*files): Import files into DB'''
        pErr = False #ProgrammingError flag
        errFiles = []
        for file in files:
            try:
                self.importData(file)
            except IOError:
                print 'File %s does not exist' % file
            except:
#                 raise #Debug
                try:
                    self.importOptin(file)
                except (sql.ProgrammingError,csv.Error) as e:
                    print 'Could not import file: {0} ({1})'.format(file,e.message)
                    errFiles.append(file)
                    pErr = True
                except:
                    raise
        if pErr:
            raise sql.ProgrammingError(','.join(errFiles))
    
    def buildStats(self):
        '''buildStats(): #Analyzes the data'''
        self.__uniqueUsers = self.calculateUniqueUsers()
        self.__payingUsers = self.calculatePayingUsers()
        self.__conversion = self.calculateConversion(self.__uniqueUsers,self.__payingUsers)
        self.__totalProceeds = self.calculateTotalProceeds()
        self.__proceedsPerUser = self.calculateProceedsPerUser(self.__totalProceeds,
                                                               self.__uniqueUsers)
        self.__clv = self.calculateCLV(self.__totalProceeds, self.__payingUsers)
        self.__currentSubscribers = self.calculateCurrentSubscribers()
        
    def writeStats(self): 
        '''writeStats(): Writes the stats into the stats table'''
        date = datetime.strftime(datetime.now(), self.__dateFormat)
        data = (date,self.__uniqueUsers,self.__payingUsers,self.__conversion,self.__totalProceeds,
                self.__proceedsPerUser,self.__clv,self.__currentSubscribers)
        with self.con:
            self.con.execute(''.join(['INSERT INTO stats VALUES (',
                                         ','.join(['?']*len(self.__statsStructure)),')']), 
                                 data)
            
    def getStats(self):
        '''getStats(): return stats tuple'''
        date = datetime.strftime(datetime.now(), self.__dateFormat)
        stats = (('Unique Users',str(self.__uniqueUsers)),
                 ('Paying Users',str(self.__payingUsers)),
                 ('Conversion',"{0:.2f}%".format(self.__conversion * 100)),
                 ('Total Proceeds',"${0:.2f}".format(self.__totalProceeds)),
                 ('Proceeds Per User',"${0:.2f}".format(self.__proceedsPerUser)),
                 ('Client Lifetime Value',"${0:.2f}".format(self.__clv)),
                 ('Current Subscribers',str(self.__currentSubscribers)))
        
        return date, stats
    
    def printStats(self):
        '''printStats(): print the stats to the stdout'''
        try:
            date, stats = self.getStats()
        except:
            raise #TODO: better exception handling
        
        print '---------------------------------'
        print ''.join(['|'.ljust(6),'Stats for ',date,'|'.rjust(7)])
        print '---------------------------------'
        for label,data in stats:
            print ''.join(['|',label.rjust(22),': ',data.ljust(7),'|'])
        print '---------------------------------'
        
    def outputStats(self,filename='stats.md'):
        '''outputStats(filename): Write current stats to external file'''
        date, stats = self.getStats()
        
        try:
            with open(filename,'w') as fp:
                fp.write(''.join(['#Stats for ',date,'\n\n']))
                for label,data in stats:
                    fp.write(''.join(['- ',label,': ',data,'\n']))
        except IOError:
            print 'Unable to write to stats file %s' % filename
            
    def setDBFile(self,file):
        '''setDBFile(file): Set the persistent DB file path'''
        with open(self.__pDBFile,'w') as fp:
            fp.write(abspath(file))
            
    def getDBFile(self):
        '''getDBFile(): Get the persistent DB file path'''
        with open(self.__pDBFile,'r') as fin:
            return fin.read()
        
    def addProduct(self,cutoffDate,product,proceeds):
        '''addProduct(cutoffDdate,product,proceeds): Add a product to the product table'''
        try:
            with self.con as c:
                c.execute('INSERT INTO product VALUES(?,?,?)',(cutoffDate,product,proceeds))
        except:
            raise #TODO: better exception handling
    
    def getProductProceeds(self,date,product):
        '''getProductProceeds(date,product): get the proceeds of a product at a certain date'''
        try:
            self.cur.execute("SELECT cutoffDate,proceeds FROM product WHERE product=?",(product,))
            data = self.cur.fetchall()
            products = [(cutoffDate,proceeds) for cutoffDate,proceeds in data if cutoffDate <= date]
            try:
                return max(products)[1] #proceeds
            except ValueError:
                print 'Could not find matching product.' 
                print 'You should add the correct product to the DB first.'
                exit(1)
        except:
            raise