# For the licence see the file : LICENCE.txt

import os, sys, functools, inspect, re, json, mimetypes

from datetime import datetime
from urlparse import urlparse
from string import Template

from django.http import HttpResponse

__all__ = ['Ext']

# Force datetime to be compatible with Json format
ExtJsonHandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None

class ExtJSError(Exception):
    
    def __init__(self, pMessage):
        self.__value = pMessage
        
    def __str__(self):
        return repr(self.__value)        

class Ext(object):

    __URLSAPI = dict()  # List of *.js file API. Each URL point to a list of class.
    __URLSRPC = dict()  # URL for RPC. Each URL point to a list of class.
    __URLSEVT = dict()  # URL for Event. Each URL point to a class.
    __METHODS = dict()  # Temporary used to build internal structur for RPC
    __EVENTS = dict()   # Temporary used to build internal structur for event

    class __Instance(object):
        pass
    
    class Json(object):
        
        @staticmethod
        def Load(pJson):
            lRet = json.loads(pJson)
            return lRet

        @staticmethod
        def Dumps(pObj):
            lRet = json.dumps(pObj,default=ExtJsonHandler)
            return lRet
        
    @staticmethod
    def sessionFromRequest(pRequest):
        return pRequest.session

    @staticmethod
    def Class(pUrlApis = None, pUrl = None, pId = None, pTimeOut = None, pNameSpace = None, pSession = None):
        
        if pId is not None and not isinstance(pId,str):
            raise ExtJSError('pId must be a string')            
        
        if pNameSpace is not None and not isinstance(pNameSpace,str):
            raise ExtJSError('pNameSpace must be a string')            
        
        if pTimeOut is not None and not isinstance(pTimeOut,int):
            raise ExtJSError('pTimeOut must be an integer')            
        
        if pUrl is not None and not isinstance(pUrl,str):
            raise ExtJSError('pUrl must be a string')            
        
        if pUrlApis is not None and not isinstance(pUrlApis,str):
            raise ExtJSError('pUrlApis must be a string')            
        
        if pSession is not None:
            if isinstance(pSession,bool) and pSession == True:
                pSession = Ext.sessionFromRequest
            elif not inspect.isfunction(pSession):
                raise ExtJSError('pSession must be method or boolean. If it\'s a method it must return a session object. If it\'s boolean with True it will return session from a django request.')

        if pUrlApis is None:
            pUrlApis = 'api.js'
        
        lExt = Ext.__Instance()
        
        lExt.UrlApis = pUrlApis
        lExt.Url = pUrl
        lExt.Id = pId
        lExt.TimeOut = pTimeOut
        lExt.NameSpace = pNameSpace
        
        def decorator(pClass):
    
            if hasattr(pClass,'__ExtJS'):
                raise ExtJSError('Class %s already register for ExtJS' % pClass.__name__)
            
            # Store ExtJS informations on the class            
            pClass.__ExtJS = lExt
            
            # Valid and store Javascript API
            if lExt.UrlApis not in Ext.__URLSAPI:
                Ext.__URLSAPI[lExt.UrlApis] = list()
            else:
                lFirstClass = Ext.__URLSAPI[lExt.UrlApis][0]
                lExtFirst = lFirstClass.__ExtJS
                if lExt.NameSpace is None:
                    # The first class has define a name space it will spread to other classes that have the same UrlApis  
                    lExt.NameSpace = lExtFirst.NameSpace
                else:
                    # For an UrlApis we must define the same name space
                    if lExt.NameSpace != lExtFirst.NameSpace: 
                        raise ExtJSError('Class "%s": A same javascript API ("%s") can not be define with two differents name space.' % (pClass.__name__,lExt.UrlApis))
                
            if lExt.Url is not None:
                lUrl = lExt.Url
            else:
                lUrl = 'Default'
                
                if lExt.NameSpace is not None:
                    lUrl = lExt.NameSpace
                
            lExt.Url = 'Rpc' + lUrl    

            if lExt.Url not in Ext.__URLSRPC:
                 Ext.__URLSRPC[lExt.Url] = dict()
                 
            Ext.__URLSRPC[lExt.Url][pClass.__name__] = pClass
            
            if pClass not in Ext.__URLSAPI[lExt.UrlApis]: 
                Ext.__URLSAPI[lExt.UrlApis].append(pClass)
            
            # Register methods
            lExt.StaticMethods = Ext.__METHODS

            # Register events
            lExt.StaticEvents = dict()

            for lKey in Ext.__EVENTS:
                lEvent = Ext.__EVENTS[lKey]
                if lEvent.ClassName is None:
                    lEvent.ClassName = pClass.__name__
                if lEvent.NameSpace is None:
                    lEvent.NameSpace = lExt.NameSpace
                if lEvent.Url is None:
                    lEvent.Url = 'Evt' + lEvent.NameSpace + lEvent.ClassName + lEvent.Name
                if lEvent.UrlApis is None:
                    lEvent.UrlApis = lExt.UrlApis
                if lEvent.Url in Ext.__URLSEVT:     
                    raise ExtJSError('Url "%s" for event "%s" already exist' % (lEvent.Url, lEvent.Name))
                Ext.__URLSEVT[lEvent.Url] = pClass
                if lEvent.UrlApis not in Ext.__URLSAPI:
                    Ext.__URLSAPI[lEvent.UrlApis] = list()
                if pClass not in Ext.__URLSAPI[lEvent.UrlApis]:
                    Ext.__URLSAPI[lEvent.UrlApis].append(pClass)
                lExt.StaticEvents[lEvent.Url] = lEvent
            
            # Apply a session method if the Session method is not already set by the method
            if pSession is not None:
                for lMethod in lExt.StaticMethods:
                    lMethodInfo = lExt.StaticMethods[lMethod] 
                    if lMethodInfo.Session is None:
                        lParams = list(lMethodInfo.Args)
                        if 'pSession' not in lParams:
                            raise ExtJSError('Method \'%s\' must declare a parameter pSession' % lMethodInfo.Name)
                        else:
                            # Check if pSession is the first parameter
                            if lParams.index('pSession') != 0:
                                raise ExtJSError('Method \'%s\' pSession must be the first parameter' % lMethodInfo.Name)
                            lParams = [lVal for lVal in lParams if lVal != 'pSession']
                            lMethodInfo.Session = pSession
                            lMethodInfo.Args = lParams
                for lEvent in lExt.StaticEvents:
                    lEventInfo = lExt.StaticEvents[lEvent] 
                    if lEventInfo.Session is None:
                        lParams = list(lEventInfo.Args)
                        if 'pSession' not in lParams:
                            raise ExtJSError('Event \'%s\' must declare a parameter pSession' % lEventInfo.Name)
                        else:
                            # Check if pSession is the first parameter
                            if lParams.index('pSession') != 0:
                                raise ExtJSError('Event \'%s\' pSession must be the first parameter' % lEventInfo.Name)
                            lParams = [lVal for lVal in lParams if lVal != 'pSession']
                            lEventInfo.Session = pSession
                            lEventInfo.Args = lParams

            Ext.__METHODS = dict()
            Ext.__EVENTS = dict()   
                
            @functools.wraps(pClass)
            def wrapper(*pArgs, **pKwargs):
                lNewObj = pClass(*pArgs,**pKwargs)
                return lNewObj
                
            return wrapper
    
        return decorator
    
    @staticmethod
    def StaticEvent(pId = None, pEventName = None, pClassName = None, pNameSpace = None, pParams = None, pInterval = None, pUrl = None, pUrlApis = None, pSession = None):
        
        # Define the provider id that will be define on the javascript side
        if pId is not None and not isinstance(pId,str):
            raise ExtJSError('pId must be a string')            
        
        # Force the event name that will be fire on the javascript side. If it's not specify the event name it's build automatically with the concatanation of
        # the name space, the classe name and the Python function name define as an event
        if pEventName is not None and not isinstance(pEventName,str):
            raise ExtJSError('pEventName must be a string')            

        # You can overwrite the classe but becarefull. The class name will be use to build the name of the event when the answer of the event it sent back.
        # If it's not specify it will take the name of the class
        if pClassName is not None and not isinstance(pClassName,str):
            raise ExtJSError('pClassName must be a string')            
        
        # pNameSpace is define to create a uniq name. Your must be sure it doesn't exist. If it's not specify it will take the name space of the class
        if pNameSpace is not None and not isinstance(pNameSpace,str):
            raise ExtJSError('pNameSpace must be a string')            
        
        # pInterval define how often to poll the server-side in milliseconds. If it's not define by default it's set to every 3 seconds by ExtJS. 
        if pInterval is not None and not isinstance(pInterval,int):
            raise ExtJSError('pInterval must be an integer')            
        
        # Specify the keywork for the URL. This keywork will be associate with the current event. The URL must be uniq for each event. 
        # By default the URL it's build like this: 'Evt' + '<Name space>' + '<Class name>' + 'Event Name' 
        if pUrl is not None and not isinstance(pUrl,str):
            raise ExtJSError('pUrl must be a string')            

        # Specify the javascript file. If it's not define it will take the same as one define for the class.
        if pUrlApis is not None and not isinstance(pUrlApis,str):
            raise ExtJSError('pUrlApis must be a string')            
        
        if pParams is not None and not (type(pParams) == list or type(pParams) == dict or type(pParams) == str or type(pParams) == int or type(pParams) == long or  type(pParams) == float):
            raise ExtJSError('pParams must be a list, dict, string, int, long or float')

        if pSession is not None:
            if isinstance(pSession,bool) and pSession == True:
                pSession = Ext.sessionFromRequest
            elif not inspect.isfunction(pSession):
                raise ExtJSError('pSession must be method or boolean. If it\'s a method it must return a session object. If it\'s boolean with True it will return session from a django request.')
        
        lEventInfo = Ext.__Instance()
        
        lEventInfo.UrlApis = pUrlApis
        lEventInfo.Url = pUrl
        lEventInfo.Id = pId
        lEventInfo.EventName = pEventName
        lEventInfo.ClassName = pClassName
        lEventInfo.NameSpace = pNameSpace
        lEventInfo.Params = pParams
        lEventInfo.Interval = pInterval
        lEventInfo.Session = pSession  
        
        def decorator(pEvent):
    
            if type(pEvent) == staticmethod:
                raise ExtJSError('You must declare @staticmethod before @Ext.StaticEvent')
    
            lArgs = inspect.getargspec(pEvent)
            lParams = list(lArgs.args)
            
            if lEventInfo.Session is not None:
                if 'pSession' not in lArgs.args:
                    raise ExtJSError('You must declare a parameter pSession')
                else:
                    # Remove pSession will be transmit automaticaly by the method Request
                    if lParams != []:
                        # Check if pSession is the first parameter
                        if lParams.index('pSession') != 0:
                            raise ExtJSError('pSession must be the first parameter')
                        lParams = [lVal for lVal in lParams if lVal != 'pSession']
                        
            lEventInfo.Name = pEvent.__name__
            lEventInfo.Args = lParams
            lEventInfo.VarArgs = lArgs.varargs
            lEventInfo.Keywords = lArgs.keywords
            lEventInfo.Defaults = lArgs.defaults
            lEventInfo.Call = pEvent
            
            Ext.__EVENTS[pEvent.__name__] = lEventInfo
        
            @functools.wraps(pEvent)
            def wrapper(*pArgs, **pKwargs):
                lRet = pEvent(*pArgs,**pKwargs)
                return lRet
                
            return wrapper
    
        return decorator

    @staticmethod
    def StaticMethod(pNameParams = False, pTypeParams = False, pSession = None):

        if not isinstance(pNameParams,bool):
            raise ExtJSError('pNameParams must be a bool. True method using naming parameters, False list of parameters')
        
        if not isinstance(pTypeParams,bool):
            raise ExtJSError('pTypeParams must be a bool. True method support type parameters, False type is not check')
        
        if pSession is not None:
            if isinstance(pSession,bool) and pSession == True:
                pSession = Ext.sessionFromRequest
            elif not inspect.isfunction(pSession):
                raise ExtJSError('pSession must be method or boolean. If it\'s a method it must return a session object. If it\'s boolean with True it will return session from a django request.')
        
        if sys.version_info < (3, 0) and pTypeParams == True:
            raise ExtJSError('Type for parameters not supported for Python %s. Must be Python 3.x' % ".".join(str(lVal) for lVal in sys.version_info))
        else:
            if pNameParams == False and pTypeParams == True:
                raise ExtJSError('Type parameters can be activated if named parameters is also activated')
        
        lMethodInfo = Ext.__Instance()
        lMethodInfo.NameParams = pNameParams
        lMethodInfo.TypeParams = pTypeParams
        lMethodInfo.Session = pSession
        
        def decorator(pMethod):
    
            if type(pMethod) == staticmethod:
                raise ExtJSError('You must declare @staticmethod before @Ext.StaticMethod')
    
            lArgs = inspect.getargspec(pMethod)
            lParams = list(lArgs.args)
            
            if lMethodInfo.Session is not None:
                if 'pSession' not in lArgs.args:
                    raise ExtJSError('You must declare a parameter pSession')
                else:
                    # Remove pSession will be transmit automaticaly by the method Request
                    if lParams != []:
                        # Check if pSession is the first parameter
                        if lParams.index('pSession') != 0:
                            raise ExtJSError('pSession must be the first parameter')
                        lParams = [lVal for lVal in lParams if lVal != 'pSession']
            
            lMethodInfo.Name = pMethod.__name__
            lMethodInfo.Args = lParams
            lMethodInfo.VarArgs = lArgs.varargs
            lMethodInfo.Keywords = lArgs.keywords
            lMethodInfo.Defaults = lArgs.defaults
            lMethodInfo.Call = pMethod
            
            Ext.__METHODS[pMethod.__name__] = lMethodInfo
        
            @functools.wraps(pMethod)
            def wrapper(*pArgs, **pKwargs):
                lRet = pMethod(*pArgs,**pKwargs)
                return lRet
                
            return wrapper
        
        return decorator

    @staticmethod
    def Request(pRequest, pRootProject = None, pRootUrl = None, pIndex = 'index.html', pAlias = None):
        lRet = HttpResponse(status = 400, content = '<h1>HTTP 400 - Bad Request</h1>The request cannot be fulfilled due to bad syntax.')

        # Remove http://<host name>:<port>/ from pRootUrl
        pRootUrl = urlparse(pRootUrl).path

        # Valid the url. 
        lPath = urlparse(pRequest.path).path
        lMatch = re.match('^/[0-9a-zA-Z\.\/\-\_]*$', lPath) 
    
        if lMatch is None:
            raise ExtJSError('You have some invalid characters on the Url: "%s"' % pRootUrl)
    
        if pRootUrl is not None:
            # If the root for the url is specify check if the Url begin with this path
            if lPath.find(pRootUrl) != 0:
                raise ExtJSError('Invalid root for the Url: "%s"' % pRootUrl)
            # Remove url root from the path
            lPath = lPath[len(pRootUrl):]
        else:
            # If url root is not specify doesn't validate it 
            pRootUrl = ''
    
        # Detect if the URL it's to return javascript wrapper        
        lUrlApis = re.search('^(\w*\.js)$', lPath)
        
        if lUrlApis is not None:
            lUrlApi = lUrlApis.group(1)
            
            if lUrlApi in Ext.__URLSAPI:
                # URL found => Generate javascript wrapper
                lRemoteAPI = dict()
                for lClass in Ext.__URLSAPI[lUrlApi]:
                    lExt = lClass.__ExtJS
                    
                    if lExt.Url not in lRemoteAPI:
                        # Collect all class with the same Url
                        lRemoteAPI[lExt.Url] = dict()
                        lCurrent = lRemoteAPI[lExt.Url]
                        if 'format' in pRequest.REQUEST and pRequest.REQUEST['format'] == 'json':
                            # 'descriptor' is need it for Sencha Architect to recognize your API
                            lCurrent['descriptor'] = lClass.__name__ + '.REMOTING_API'
                            if lExt.NameSpace is not None:
                                 lCurrent['descriptor'] = lExt.NameSpace + '.' + lCurrent['descriptor']
                        lCurrent['url'] = lExt.Url
                        lCurrent['type'] = 'remoting'
                        if lExt.Id is not None:
                            lCurrent['id'] = lExt.Id
                        if lExt.NameSpace is not None:
                            lCurrent['namespace'] = lExt.NameSpace
                        lCurrent['actions'] = dict()
                        lAction = lCurrent['actions']
                    
                    if len(lExt.StaticMethods) > 0:
                        # Define a class as an Action with a list of functions
                        lRemoteMethods = list()
                        for lMethod in lExt.StaticMethods:
                            lMethodInfo = lExt.StaticMethods[lMethod]
                            if not lMethodInfo.NameParams:
                                lMethodExt = dict(name = lMethod, len = len(lMethodInfo.Args))
                            else:
                                # Type not supported with python 2.7 or lower.
                                if sys.version_info < (3, 0):
                                    lMethodExt = dict(name = lMethod, params = lMethodInfo.Args)
                                else:
                                    if not lMethodInfo.TypeParams:
                                        lMethodExt = dict(name = lMethod, params = lMethodInfo.Args)
                                    else:
                                        # TODO: support this feature for python 3.x
                                        # Must return something like this :
                                        #    "params": [{
                                        #    "name": "path",
                                        #    "type": "string",
                                        #    "pos": 0
                                        #    },
                                        raise ExtJSError('Type for parameters not supported yet')
                            lRemoteMethods.append(lMethodExt)
                        # Each class is define as an 'Action' 
                        lAction[lClass.__name__] = lRemoteMethods
                    for lKey in lExt.StaticEvents:
                        # Each event is define as a Provider for ExtJS. Even if it share the same namespace.
                        lEvent = lExt.StaticEvents[lKey]
                        lRemote = dict()
                        lRemote['url'] = lEvent.Url
                        lRemote['type'] = 'polling'
                        if lEvent.Id is not None:
                            lRemote['id'] = lEvent.Id
                        if lEvent.NameSpace is not None:
                            lRemote['namespace'] = lEvent.NameSpace
                        if lEvent.Params is not None:
                            lRemote['baseParams'] = lEvent.Params
                        if lEvent.Interval is not None:
                            lRemote['interval'] = lEvent.Interval
                        lRemoteAPI[lEvent.Url] = lRemote

                if len(lRemoteAPI) > 0:    
                    lJsonRemoteAPI = json.dumps(lRemoteAPI.values(),default=ExtJsonHandler)
                    
                    lNameSpace = lClass.__name__
                    if lExt.NameSpace is not None:
                        lNameSpace = lExt.NameSpace + '.' + lNameSpace
                    
                    if 'format' in pRequest.REQUEST and pRequest.REQUEST['format'] == 'json':
                        # Define JSON format for Sencha Architect
                        lContent = 'Ext.require(\'Ext.direct.*\');Ext.namespace(\''+ lNameSpace +'\');'+ lNameSpace + '.REMOTING_API = ' + lJsonRemoteAPI[1:len(lJsonRemoteAPI)-1] + ';'
                    else:
                        # Otherwise it's return a Javascript. Each javascript must be include under the index.html like this:
                        # <script type="text/javascript" src="api.js"></script>
                        # Automatically your API is declare on ExtJS and available on your app.js. 
                        lContent = 'Ext.require(\'Ext.direct.*\');Ext.namespace(\''+ lNameSpace +'\');Ext.onReady( function() { Ext.direct.Manager.addProvider(' + lJsonRemoteAPI[1:len(lJsonRemoteAPI)-1] + ');});'
                    lRet = HttpResponse(content = lContent, mimetype='application/javascript')
        else:
            # Detect if the URL it's a RPC or a Poll request
            lUrlRPCsorPolls = re.search('^(\w*)$', lPath)
        
            if lUrlRPCsorPolls is not None:
                lUrl = lUrlRPCsorPolls.group(1)
                
                if lUrl in Ext.__URLSRPC:
                    
                    # URL recognize as a RPC
                    
                    # Extract data from raw post. We can not trust pRequest.POST
                    lReceiveRPCs = json.loads(pRequest.body)
                    
                    # Force to be a list of dict
                    if type(lReceiveRPCs) == dict:
                        lReceiveRPCs = [lReceiveRPCs]
                    
                    # Extract URL 
                    lClassesForUrl = Ext.__URLSRPC[lUrl]

                    # Initialize content
                    lContent = list()

                    for lReceiveRPC in lReceiveRPCs:
                        # Execute each RPC request
                        
                        lRcvClass = lReceiveRPC['action']
                        lRcvMethod = lReceiveRPC['method']

                        # Create name API
                        lMethodName = lRcvClass + '.' + lRcvMethod
                            
                        # Prepare answer
                        lAnswerRPC = dict(type = 'rpc', tid = lReceiveRPC['tid'], action = lRcvClass, method = lRcvMethod)
                        
                        # Prepare exception
                        lExceptionData = dict(Url = lUrl, Type = 'rpc', Tid = lReceiveRPC['tid'], Name = lMethodName )
                        lException = dict(type = 'exception', data = lExceptionData, message = None)
                        
                        if lRcvClass in lClassesForUrl:
                            
                            # URL for RPC founded
                            lClass = lClassesForUrl[lRcvClass]
                            lExt = lClass.__ExtJS
                            
                            if lRcvMethod in lExt.StaticMethods:
                                
                                # Method founded
                                lMethod = lExt.StaticMethods[lRcvMethod]
                                
                                # Name used for exception message
                                if lExt.NameSpace is not None:
                                    lMethodName = lExt.NameSpace + '.' + lMethodName 

                                # Add Id if it's define
                                if lExt.Id is not None:
                                    lExceptionData['Id'] = lExt.Id
                                
                                # Extract datas
                                lArgs = lReceiveRPC['data']
                                
                                # Control and call method  
                                if lArgs is None:
                                    if len(lMethod.Args) != 0:
                                        lException['message'] = '%s numbers of parameters invalid' % lMethodName
                                    else:
                                        try:
                                            # Call method with no parameter
                                            if lMethod.Session is None:
                                                lRetMethod = lMethod.Call()
                                            else:
                                                lRetMethod = lMethod.Call(pSession = lMethod.Session(pRequest))
                                            if lRetMethod is not None:
                                                lAnswerRPC['result'] = lRetMethod
                                        except Exception as lErr:
                                            lException['message'] = '%s: %s' % (lMethodName, str(lErr)) 
                                elif type(lArgs) == list:
                                    if len(lArgs) > len(lMethod.Args):
                                        lException['message'] = '%s numbers of parameters invalid' % lMethodName
                                    else:
                                        try:
                                            # Call method with list of parameters  
                                            if lMethod.Session is None:
                                                lRetMethod = lMethod.Call(*lArgs)
                                            else:
                                                lArgs.insert(0,lMethod.Session(pRequest))
                                                lRetMethod = lMethod.Call(*lArgs)
                                            if lRetMethod is not None:
                                                lAnswerRPC['result'] = lRetMethod
                                        except Exception as lErr:
                                            lException['message'] = '%s: %s' % (lMethodName, str(lErr)) 
                                elif type(lArgs) == dict:
                                    if not lMethod.NameParams:
                                        lException['message'] = '%s does not support named parameters' % lMethodName
                                    else: 
                                        if len(lArgs.keys()) > len(lMethod.Args):
                                            lException['message'] = '%s numbers of parameters invalid' % lMethodName
                                        else:
                                            lInvalidParam = list()
                                            for lParam in lArgs:
                                                if lParam not in lMethod.Args:
                                                     lInvalidParam.append(lParam)
                                            if len(lInvalidParam) > 0:
                                                lException['message'] = '%s: Parameters unknown -> %s' % ",".join(lInvalidParam) 
                                            else:
                                                try:
                                                    # Call method with naming parameters
                                                    if lMethod.Session is None:
                                                        lRetMethod = lMethod.Call(**lArgs)
                                                    else:
                                                        lArgs['pSession'] = lMethod.Session(pRequest)
                                                        lRetMethod = lMethod.Call(**lArgs)
                                                    if lRetMethod is not None:
                                                        lAnswerRPC['result'] = lRetMethod
                                                except Exception as lErr:
                                                    lException['message'] = '%s: %s' % (lMethodName, str(lErr))
                            else:
                                lException['message'] = '%s: API not found' % lMethodName
                                
                        else:
                            lException['message'] = '%s: API not found' % lMethodName
                                
                        if lException['message'] is not None:
                            lContent.append(lException)    
                        else:
                            lContent.append(lAnswerRPC)
                            
                    if len(lContent) > 0:
                        if len(lContent) == 1:
                            lRet = HttpResponse(content = json.dumps(lContent[0],default=ExtJsonHandler), mimetype='application/json')
                        else:
                            lRet = HttpResponse(content = json.dumps(lContent,default=ExtJsonHandler), mimetype='application/json')
                                
                elif lUrl in Ext.__URLSEVT:

                    # URL Recognize as Poll request. A poll request will be catch by an Ext.StaticEvent.
                    
                    lClass = Ext.__URLSEVT[lUrl]
                    lExt = lClass.__ExtJS
                    
                    lEvent = lExt.StaticEvents[lUrl]
                    
                    # Define the name of the event this will be fire on ExtJS
                    if lEvent.EventName is not None:
                        # Use the one specify with @Ext.StaticEvent parameter pEventName
                        lEventName = lEvent.Name
                    else: 
                        # This name is build with the concatanation of the name space, classe name and name event
                        lEventName = lEvent.Name
                        
                        if len(lEvent.ClassName) != 0:
                            lEventName = lEvent.ClassName + '.' + lEvent.Name
                        
                        if len(lEvent.NameSpace) != 0:
                            lEventName = lEvent.NameSpace + '.' + lEventName
                        
                    # Prepare event answer
                    lAnswerEvent = dict(type = 'event', name = lEventName, data = None)
                    
                    # Prepare exception 
                    #  Data exception have the same structur as define for a method except we don't have Tid information. It set to -1. 
                    lExceptionData = dict(Url = lUrl, Type = 'event', Tid = -1, Name = lEventName )
                    lException = dict(type = 'exception', data = lExceptionData, message = None)
                    
                    # Add Id if it's define. With the id on your javascript code you can use something like this:
                    # Ext.direct.Manager.on('exception', function(e) {
                    # if (e.data.Type == 'event') 
                    #    {
                    #      lPoll = Ext.direct.Manager.getProvider(e.data.Id);
                    #       lPoll.disconnect();
                    #    }        
                    # }
                    if lEvent.Id is not None:
                        lAnswerEvent['Id'] = lEvent.Id
                        lExceptionData['Id'] = lEvent.Id
                    
                    # Extraction of parameters. For event parameters are in the POST. 
                    # If for a key we don't have a value than mean we received a simple list of parameters direct under the key.
                    # If the key have a value that mean we have naming parameters
                    lArgs = None
                    for lKey in pRequest.POST:
                        if pRequest.POST[lKey] == '':
                            if lArgs is None:
                                lArgs = list()
                            lArgs.extend(lKey.split(','))
                        else:
                            if lArgs is None:
                                lArgs = dict()
                            lArgs[lKey] = pRequest.POST[lKey] 
                    
                    # Control and call event  
                    if lArgs is None:
                        if len(lEvent.Args) != 0:
                            lException['message'] = '%s numbers of parameters invalid' % lEventName
                        else:
                            try:
                                # Call event with no parameter
                                if lEvent.Session is None:
                                    lRetEvt = lEvent.Call()
                                else:
                                    lRetEvt = lEvent.Call(pSession = lEvent.Session(pRequest))
                                if lRetEvt is not None:
                                    lAnswerEvent['data'] = lRetEvt
                            except Exception as lErr:
                                lException['message'] = '%s: %s' % (lEventName, str(lErr)) 
                    elif type(lArgs) == list:
                        if len(lArgs) > len(lEvent.Args):
                            lException['message'] = '%s numbers of parameters invalid' % lEventName
                        else:
                            try:
                                # Call event with list of parameters  
                                if lEvent.Session is None:
                                    lRetEvt = lEvent.Call(*lArgs)
                                else:
                                    lArgs.insert(0,lEvent.Session(pRequest))
                                    lRetEvt = lEvent.Call(*lArgs)
                                if lRetEvt is not None:
                                    lAnswerEvent['data'] = lRetEvt
                            except Exception as lErr:
                                lException['message'] = '%s: %s' % (lEventName, str(lErr)) 
                    elif type(lArgs) == dict:
                        if len(lArgs.keys()) > len(lEvent.Args):
                            lException['message'] = '%s numbers of parameters invalid' % lEventName
                        else:
                            lInvalidParam = list()
                            for lParam in lArgs:
                                if lParam not in lEvent.Args:
                                     lInvalidParam.append(lParam)
                            if len(lInvalidParam) > 0:
                                lException['message'] = '%s: Parameters unknown -> %s' % ",".join(lInvalidParam) 
                            else:
                                try:
                                    # Call event with naming parameters
                                    if lEvent.Session is None:
                                        lRetEvt = lEvent.Call(**lArgs)
                                    else:
                                        lArgs['pSession'] = lEvent.Session(pRequest)
                                        lRetEvt = lEvent.Call(**lArgs)
                                    if lRetEvt is not None:
                                        lAnswerEvent['data'] = lRetEvt
                                except Exception as lErr:
                                    lException['message'] = '%s: %s' % (lEventName, str(lErr)) 
                                
                    if lException['message'] is not None:
                        lContent = lException    
                    else:
                        lContent = lAnswerEvent
                    
                    lRet = HttpResponse(content = json.dumps(lContent,default=ExtJsonHandler), mimetype='application/json')
    
        if lRet.status_code != 200:
            # The URL is not to return the API, not to execute a RPC or an event. It's just to get a file
            if pRootProject is not None:
                if not os.path.exists(pRootProject):
                    raise ExtJSError('Invalid root for the project: "%s"' % pRootProject)
            else:
                # if the root project is not specify get the path of the current folder
                pRootProject = os.getcwd()
        
            # The path is empty try to find and load index.html (or the file specify with pIndex)   
            if len(lPath) == 0:
                lPath = pIndex
    
            # Rebuild path to valid it         
            lPath = os.path.normpath("/".join([pRootProject,lPath]))
            lFileName, lFileExt = os.path.splitext(lPath)
           
            # Check if the path exist and if the extension is valid
            if not os.path.exists(lPath):
                raise ExtJSError('File not found: "%s"' % lPath)
            else:
                if lFileExt not in ['.html','.css','.js','.png','.jpg','.gif','.json','.xml']:
                    raise ExtJSError('File extension is invalid: "%s"' % lFileExt)
                else:
                    try:
                        lMime = mimetypes.types_map[lFileExt]
                    except Exception as lException:
                        if isinstance(lException,KeyError) and lFileExt == '.json':
                            lMime = 'text/json'
                        else:
                            raise lException
                    # TODO: Manage a chache file
                    lFile = open(lPath)
                    lContent = lFile.read()
                    lFile.close()
                    lRet = HttpResponse(content = lContent, mimetype = lMime)
              
        return lRet
