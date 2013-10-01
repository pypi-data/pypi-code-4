import urllib2
from bs4 import BeautifulSoup as Broth

def retrieve_url (url):

   """
    To retrive the contents of url .
    The url must be in some valid format :
         * http://www.example.com/.
         * https://www.example.com/  """


   opener = urllib2.build_opener ()    
   try:
        t = opener.open (url).read ()
        parser = Broth(t)
        l =[x['href'] for x in parser.findAll ('a') \
                if x.has_attr ('href')]
        return l
   except urllib2.URLError:
      print ("Error accessing URL. Check your Internet connection")
      return []
   except ValueError:
        return []
