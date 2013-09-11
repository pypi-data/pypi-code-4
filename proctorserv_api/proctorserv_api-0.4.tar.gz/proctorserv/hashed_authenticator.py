import requests
import random
import hashlib
import time
from collections import OrderedDict

class HashedAuthenticator(object):

  @classmethod
  def apply_reverse_guid_and_sign(cls, params, customer_identifier, shared_secret):
    params['guid'] = str(random.getrandbits(64))
    params['customer_id'] = customer_identifier
    query_string = cls.create_query_string(params) + shared_secret
    params['guid'] = params['guid'][::-1]
    params['signature'] = hashlib.sha256(query_string).hexdigest() 
    return params['signature']

  @classmethod  
  def create_query_string(cls, options):
    combined_options = []
    for key, value in options.iteritems():
      sval = str(value).lower() if isinstance(value, bool)  else str(value)
      combined_options.append(key + '=' + sval)

    return "&".join(combined_options)


