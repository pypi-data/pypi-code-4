""" This is a python wrapper for "New york times" api """

import nytimes_article_search

__all__ = ["nytimes_article_search"]

def get_article_search_obj(search_api_key):
  
  """ This function initializes an object of type "article_search.It takes in as a parameter the search_api_key.
  You have to pass in a valid nytimes "article_search api key". You can obtain a valid article search api key by
  registering at 'https://myaccount.nytimes.com/auth/login?URI=http://developer.nytimes.com/login/external'

  Return type: article_search 
  Using the returned object, you can search nytimes for relevant articles.
  
  """
  
  return nytimes_article_search.articleSearch(search_api_key)



if __name__ == "__main__":
  print "Please import this module in a script to use it."
  exit(0)

