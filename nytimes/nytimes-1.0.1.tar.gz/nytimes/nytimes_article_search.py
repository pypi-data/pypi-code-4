""" Python wrapper for the article search api [version 2] of "The New York times """

import sys

try:
  import requests
except ImportError:
  print "ImportError: module 'requests' not found!"
  sys.exit(1)

try:
  import json
except ImportError:
  print "ImportError: module 'json' not found!"
  sys.exit(1)


article_search_base_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json"


class articleSearch:

  @staticmethod
  def checkData(**data):
    """ Utility method to check the response got back """
    if "errors" in data.keys():
      print data["status"]
      print data["errors"]
      sys.exit(1)
  
  def __init__(self,api_key):
    """ Initialize the api-key here """
    self.api_key = api_key;
    self.payload = {}
    return;

  def article_search(self,filename=None,**kwargs):

    """
    This function provides a wrapper around the "New york times" article search api.
    Parameters can be passed in as keyword arguments.For a complete list of the keyword arguments
    that can be passed refer to the documentation at the newyork times developer site.

    Additionally you can specify a file name to save the serach results in json format.If no filename
    is given, then this function will return a dictionary object.
    
    NOTE: You can also provide a different article search apikey each time as a keyword argument.
    
    """
   
    self.payload = {} 
    self.payload["api-key"] = self.api_key
    
    for key in kwargs.keys():      
      self.payload[key] = kwargs[key]
      
    r = requests.get(article_search_base_url,params=self.payload)
    rawData = json.loads(r.text)
    
    # Validate the data 
    self.checkData(**rawData)
    
    if filename is None:
      return rawData
    else:
      with open(filename,mode='w') as fileH:
        json.dump(rawData,fileH,indent=4)
        

  def article_search_simple(self,q,filename=None,num_pages=1):
    
    """
    This function adds a default filter to the search query sent over to nytimes server and returns
    only the following fields: web_url,snippet,lead_paragraph,abstract,blog,source,headline and pub_date.

    This function accepts a query string and returns a list of dictionary objects for the search results.
    However, if you psecify a filename, the search results will be saved in a json format.
    
    You can also specify the number of pages of results to be retrieved, using numpages = n
    

    """

    self.payload = {}
    list_of_pages = []
    write_to_file = False
    
    # Make sure to open and tuncate the file it it exists.
    if filename is not None:
      try:
        with open(filename,mode='w'):
          write_to_file = True
      except IOError:
        print "Unable to open file:%s for write" % (filename)

    self.payload["q"]=" ".join(q.split(','))
    self.payload["api-key"] = self.api_key
    self.payload["fl"]="web_url,snippet,lead_paragraph,abstract,blog,source,headline,pub_date"

     
    for page in xrange(num_pages):
      self.payload['page']=page
      r = requests.get(article_search_base_url,params=self.payload)
      rawData = json.loads(r.text)
      self.checkData(**rawData)
      processedData = rawData["response"]["docs"]
      
      if write_to_file:
        with open(filename,mode="a") as fileH:
          json.dump(processedData,fileH,indent = 4)
      else:
        list_of_pages.append(json.dumps(processedData,ensure_ascii=False,indent=2))

    if write_to_file == False:
      return list_of_pages
    else:
      return

  def article_search_frontpage(self,q=None,num_pages=1,begin_date=None,end_date=None,filename=None):
    
    """
    This function lets you specify a string of comma seperated words,and search for front page
    articles containing them. Additionally you can specify the following:

    begin_date -> start date of publication to search from
    end_date   -> End date of publication to stop at
    filename   -> filename to log the results, if the file exists, it will be overwritten
    num_pages   -> Number of pages of results wanted 

    """
    self.payload = {}
    list_of_pages = []
    write_to_file = False

    # Truncate the file to zero length if the file already exists 
    if filename is not None:
      try:
        with open(filename,mode='w'):
          write_to_file = True
      except IOError:
        print "Unable to open file:%s" % (filename)
          
    if begin_date is not None:
      self.payload["begin_date"]=begin_date

    if end_date is not None:
      self.payload["end_date"] = end_date
      
    # Process the list of words here
    if q is not None:
      string = " ".join(q.split(','))
      self.payload["fq"] = string+" AND "+"type_of_material:(\"Front Page\")"

    self.payload["api-key"] = self.api_key  
  
     
    for page in xrange(num_pages):
      self.payload['page'] = page
      r = requests.get(article_search_base_url,params = self.payload)
      rawData = json.loads(r.text)
      self.checkData(**rawData)
      processedData = rawData["response"]["docs"]
      if write_to_file:
        with open(filename,mode="a") as fileH:
          json.dump(processedData,fileH,indent = 4)
      else:
        list_of_pages.append(json.dumps(processedData,ensure_ascii=False,indent=2))
         
    if write_to_file == False:
      return list_of_pages
    else:
      return
      
