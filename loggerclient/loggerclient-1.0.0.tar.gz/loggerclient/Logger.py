import urllib
import urllib2
import json

class Logger:
  version = '1.0.0'
  
  api_key = None
  
  base_uri = 'http://getlogger.com/logger/%s/'
  
  @staticmethod
  def init(api_key):
    Logger.api_key = api_key
  
  @staticmethod
  def getAPIURI():
    if not Logger.api_key:
      raise Exception("No API key set")
    
    return Logger.base_uri % (Logger.api_key)
  
  @staticmethod
  def sendMessage(options):
    try:
      data = urllib.urlencode(options)
      request = urllib2.Request(Logger.getAPIURI(), data)
      response = urllib2.urlopen(request).read()
      jResponse = json.loads(response)
      
      if jResponse['success']:
        return True
      else:
        return False
    except:
      pass
      # return False
  
  @staticmethod
  def error(message):
    return Logger.sendMessage({
      'type'    : 'error',
      'message' : message,
      'version' : Logger.version
    })
  
  @staticmethod
  def warn(message):
    return Logger.sendMessage({
      'type'    : 'warn',
      'message' : message,
      'version' : Logger.version
    })
  
  @staticmethod
  def info(message):
    return Logger.sendMessage({
      'type'    : 'info',
      'message' : message,
      'version' : Logger.version
    })
  
  @staticmethod
  def log(message):
    Logger.info(message)

