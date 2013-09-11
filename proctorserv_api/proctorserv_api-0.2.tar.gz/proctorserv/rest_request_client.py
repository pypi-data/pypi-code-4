from hashed_authenticator import HashedAuthenticator
import requests
import json

class RestRequestClient:

  def make_get_request(self, url, customer_identifier, shared_secret, params):
    """ Makes a HTTP GET request with the proper user information """
    HashedAuthenticator.apply_reverse_guid_and_sign(params, customer_identifier, shared_secret)
    response = requests.get(url, params=params) 
    return response


  def make_post_request(self, url, customer_identifier, shared_secret, params):
    """ Makes a HTTP POST request with the proper user information """
    HashedAuthenticator.apply_reverse_guid_and_sign(params, customer_identifier, shared_secret)
    response = requests.post(url, data=params)
    return response



