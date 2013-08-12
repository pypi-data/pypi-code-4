import urllib, requests, json

from errors import NoApiTokenProvidedException, MissingArgumentException

"""
Fosbury Python Client
"""

__version__ = '0.9'
__author__ = 'Willem Spruijt <willem@fosbury.co>'

class Client():
    """Initialize the Fosbury client"""
    def __init__(self, api_token=None, endpoint=None):
      self.api_token = api_token
      self.endpoint = "https://app.fosbury.co/api/v1/" if endpoint == None else endpoint

    def get_templates(self):
      return self.get("templates")
    
    def get_campaigns(self):
      return self.get("campaigns")
    
    def get_passes(self):
      return self.get("passes")
    
    def get_template(self, id):
      return self.get("templates/" + str(id))
    
    def get_campaign(self, id):
      return self.get("campaigns/" + str(id))
    
    def get_pass(self, id):
      return self.get("passes/" + str(id))

    def create_template(self, name, style, options={}):
      options['name'] = name
      options['style'] = style

      return self.post("templates", options)

    def create_campaign(self, template_id, options={}):
      options['template_id'] = template_id
      return self.post("campaigns", options)

    def create_pass(self, campaign_id, options={}):
      if campaign_id is None:
        raise MissingArgumentException('Please provide a campaign_id')

      options['campaign_id'] = campaign_id
      return self.post("passes", options)

    def update_template(self, template_id, options={}):
      if template_id is None:
        raise MissingArgumentException('Please provide a template_id')

      return self.put("tempates/" + template_id, options)

    def update_campaign(self, campaign_id, options={}):
      if campaign_id is None:
        raise MissingArgumentException('Please provide a campaign_id')

      return self.put("campaigns/" + campaign_id, options)

    def update_pass(self, pass_id, options={}):
      if pass_id is None:
        raise MissingArgumentException('Please provide a pass_id')

      return self.put("passes/"+ str(pass_id), options)

    def delete_template(self, teplate_id):
      return self.delete("tempates/" + str(template_id))

    def delete_campaign(self, campaign_id):
      return self.delete("campaigns/" + str(template_id))

    def delete_pass(self, pass_id):
      return self.delete("passes/" + str(pass_id))

    def push_pass(self, pass_id, options={}):
      return self.put("passes/" + str(pass_id) + "/push", options)
    
    def distribute_campaign(self, campaign_id):
      return self.post("campaigns/" + str(campaign_id) + "/distribute")
    
    def get_campaign_locations(self, campaign_id):
      return self.get("/campaigns/" + str(campaign_id) + "/locations")

    def create_campaign_location(self, campaign_id, lat, lng, name, address=''):
      options = { 'campaign_id': campaign_id, 'lat': lat, 'long': lng, 'name': name, 'address': address }
      return self.post("campaigns/" + str(campaign_id) + "/locations", options)
    
    def delete_campaign_location(self, campaign_id, location_id):
      return self.delete("campaigns/" + str(campaign_id) + "/locations/" + str(location_id))
    
    def get_campaign_backfields(self, campaign_id):
      return self.get("campaigns/" + str(campaign_id) + "/backfields")
    
    def create_campaign_backfield(self, campaign_id, title, description):
      options = { 'title': title, 'description': description }
      return self.post("campaigns/" + str(campaign_id) + "/backfields", options)
    
    def delete_campaign_backfield(self, campaign_id, backfield_id):
      return self.delete("campaigns/" + str(campaign_id) + "/backfields/" + str(backfield_id))

    def get(self, url):
      r = requests.get(self.endpoint + url, headers=self.get_headers())
      return self.parse_json(r)

    def post(self, url, post_params):
      r = requests.post(self.endpoint + url, data=self.construct_payload(post_params), headers=self.get_headers())
      return self.parse_json(r)

    def put(self, url, post_params):
      r = requests.put(self.endpoint + url, data=self.construct_payload(post_params), headers=self.get_headers())
      return self.parse_json(r)

    def delete(self, url):
      r = requests.delete(self.endpoint + url, headers=self.get_headers())
      return self.parse_json(r)

    def construct_payload(self, params):
      return urllib.urlencode(params)

    def get_headers(self):
      if self.api_token is None:
        raise NoApiTokenProvidedException("No authentication token provided.") 
      return {'X-Fosbury-Token': self.api_token}

    def parse_json(self, response_object):
      if len(response_object.text.strip()) is not 0:
        return response_object.json()
      else:
        return json.dumps({})