import json


intDict = {}
objDict = {}
respDict = {}
cmiDict = {}
index = 0
count = 0


lmsDict = {"completion_status":"cmi.completion_status",
           "credit":"cmi.credit",
           "entry":"cmi.entry",
           "exit":"cmi.exit",
           "location":"cmi.location",
           "mode":"cmi.mode",
           "score_raw":"cmi.score_raw",
           "score_min":"cmi.score_min",
           "score_max":"cmi.score_max",
           "success_status":"cmi.success_status",
           


          }

def updateDict():
  global intDict,objDict,respDict
  intDict = { "@id":"cmi.interactions.%s.id" %(index),
           "type":"cmi.interactions.%s.type" %(index),
           "weighting":"cmi.interactions.%s.weighting:" %(index),
           "learner_response":"cmi.interactions.%s.learner_response" %(index),
           "result":"cmi.interactions.%s.result"%(index),
           "description":"cmi.interactions.%s.description" %(index)
  
          }
  objDict = { "@id" : "cmi.interactions.%s.objectives.0.id" %(index)}
  respDict= {"@id" : "cmi.interactions.%s.correct_responses.0.pattern" %(index)}     

          

def recurse(d,key=None):
    
    if type(d)==type({}) or type(d)==type([]):
      for k in d:
        if type(d[k]) != type({}) and type(d[k])!=type([]):
          cmiMapper(k,key,d[k])	
        elif type(d[k]) == type ([]):
          for i in range(len(d[k])):
            recurse(d[k][i],k)
         
        else:    
          recurse(d[k],k)
           
    else:
  	 pass
 
def performIndexing():
    global count,index
    count = count +1
    if count > 8:
      count = 1
      index = index +1
      updateDict()  
     

def cmiMapper(childKey,parentKey,childval):
    global count,cmiDict
    if parentKey == "interaction" and  count <=8:
        
        if childKey in intDict.keys():
            performIndexing()
            cmiDict[intDict[childKey]] = childval
    elif parentKey == "objective" and  count <=8 and childval != "":
               
        if childKey in objDict.keys():
            performIndexing()
            cmiDict[objDict[childKey]] = childval   
    elif parentKey == "response" and  count <=8:
         
        if childKey in respDict.keys():
           performIndexing()
           cmiDict[respDict[childKey]] = childval   
    else:
        if childKey in lmsDict.keys():
            cmiDict[lmsDict[childKey]] = childval            
        else:
          return    


def jsonToCmiJson(filename):
  initVars()
  try:
    f= open(filename,'r')
    data = json.load(f)
  except IOError:
    logger.debug('Error: Unable to open file')      
  updateDict()    
  recurse(data)  
  cmiJson=  json.dumps(cmiDict, sort_keys = True, indent = 4)
  return cmiJson
  
def initVars():
  global cmiDict,count,index
  cmiDict = {} 
  count = 0
  index = 0