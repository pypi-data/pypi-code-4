import requests

class IfbyphoneApiBase(object): 
    
    options = {}
    
    base_url = 'https://secure.ifbyphone.com/'
    
    def __init__(self, client):
        self.key = client.get_key()
    
    def call(self, args, end_point=None, key_param=None):
        """ Method for executing HTTP request
        """
        if end_point is None:
            end_point = 'ibp_api.php'
        
        if key_param is None:
            key_param = 'api_key'
        
        self.options[key_param] = self.key
            
        url = self.get_url(end_point)
        r = requests.get(url, params=args)
        return r.text
    
    def get_url(self, end_point):
        return self.base_url + end_point