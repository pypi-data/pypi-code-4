"""
CRUD - Create, Read, Update, Delete
   Resource interface.

Creating a CRUD finder

   crud = mySqlCrud()
   crud.connectInfo("host", "user", "passwd", "db)
   crud.addQuery("allBooks", "select * from Books")
   crud.addQuery("oneBookByIsbn", "select * from Books where Isbn=%s")
   (XXXX ... should figure out how to make the %s into ? for non-mysql...)
"""

import types
from whiff.rdjson import jsonParse

CONNECTION_QUERY = "CONNECTION"

class mySqlCrud:
    "CRUD resource for MySql databases"
    # this class is designed to be easily subclassed for other SQL databases.
    def __init__(self):
        "initialize data structures"
        # Test query used to determine if tables need creating.
        # Executing this statement should raise an exception if
        # the database is not initialized.
        self.testQueryStatement = None
        # This is this list of statements used to create the database.
        self.createStatementList = []
        # Mapping of names to allowed query operations.
        self.nameToQueryStatement = {}
        # Mapping of names to allowed update operations.
        self.nameToUpdateStatement = {}
        # The database connection (for one request).
        self.connection = None
        # The information for establishing a database connection
        self.connectInfo()

    def addCreateStatement(self, stmt):
        self.createStatementList.append(stmt)
        
    def addQuery(self, name, query):
        assert name!=CONNECTION_QUERY, "reserved query name, cannot redefine "+repr(name)
        self.nameToQuery[name] = query
        
    def addUpdate(self, name, query):
        self.nameToUpdateStatement[name] = query
        
    def addTestQuery(self, stmt):
        self.testQueryStatement = stmt
        
    def connectInfo(self, host=None, user=None, passwd=None, db=None):
        "record information required for establishing a mySql connection"
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.connection = None
        
    def clone(self):
        "copy database connection information"
        result = mySqlCrud()
        result.connectInfo(self.host, self.user, self.passwd, self.db)
        
    def localize(self, env):
        "return a connected instance to handle a request, execute create statements if needed"
        # copy database information data structures to new instance
        result = self.clone()
        result.createStatementList = list(self.createStatementList)
        result.nameToQuery = self.nameToQuery.copy()
        result.nameToUpdateStatement = self.nameToUpdateStatement.copy()
        # connect the instance
        result.getConnection()
        # initialize the database if needed
        result.initializeDatabase()
        # return the connected and initialized resource finder
        return result
    
    def get(self, pathlist):
        lpt = len(pathlist)
        assert lpt>0, "get requires query name"
        queryName = pathlist[0]
        # special case: return connection
        if queryName==CONNECTION_QUERY:
            return self.getConnection()
        startIndex = endIndex = None
        arguments = ()
        if lpt>1:
            arguments = pathlist[1]
        if lpt>2:
            startIndex = pathlist[2]
        if lpt>3:
            endIndex = pathlist[3]
        assert lpt<=4, "expect only name, arguments (optional), start (optional), end (optional); got too many "+repr(pathlist)
        stmt = self.nameToQuery.get(queryName)
        assert query is not None, "unknown query name "+repr(queryName)
        result = self.executeQuery(stmt, arguments, startIndex, endIndex)
        return result
    
    def put(self, pathlist, value):
        lpt = len(pathlist)
        assert lpt==1, "put expects a name only "+repr(pathlist)
        statementName = pathlist[0]
        # if value is a string convert it to json
        if type(value) in types.StringTypes:
            value = value.strip()
            if value:
                (flag, jsonvalue, cursor) = jsonParse.parseValue(value)
                assert flag, "could not interpret string as json value "+repr(value.strip[:80])
                value = jsonvalue
            else:
                value = () # empty string means no arguments
        arguments = value
        stmt = self.nameToUpdateStatement.get(statementName)
        assert stmt is not None, "no such update operation registered "+repr(statementName)
        self.executeStatement(stmt, arguments)
        
    def getConnection(self):
        # get the cached connection to the database (or get it and cache it if not set up yet).
        if self.connection is None:
            import mySQLdb
            self.connection = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
        return self.connection
    
    def initializeDatabase(self):
        try:
            self.executeQuery(self.testQueryStatement)
        except:
            # if anything goes wrong, try to create the database
            for stmt in self.createStatementList:
                self.executeStatement(stmt)
                
    def executeStatement(self, stmt, arguments=()):
        connection = self.getConnection()
        cursor = connection.cursor()
        arguments = tuple(arguments)
        cursor.execute(stmt, arguments)
        return cursor
    
    def executeQuery(self, stmt, arguments=(), startIndex=None, endIndex=None):
        cursor = self.executeStatement(stmt, arguments)
        results = cursor.fetchall()
        length = len(results)
        if endIndex:
            results = result[:endIndex]
        else:
            endIndex = length
        if startIndex:
            results = results[startIndex:]
        else:
            startIndex = 0
        # translate to dictionaries
        description = cursor.description
        Dresults = {}
        for r in results:
            D = {}
            count = 0
            for desc in description:
                name = desc[0]
                D[name] = r[count]
                count += 1
            Dresults.append(D)
        Dresults["length"] = length
        Dresults["startIndex"] = startIndex
        Dresults["endIndex"] = endIndex
        return Dresults
    

