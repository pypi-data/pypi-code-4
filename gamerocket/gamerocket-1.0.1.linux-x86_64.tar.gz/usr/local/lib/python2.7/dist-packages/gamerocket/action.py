from configuration import Configuration
from resource import Resource

class Action(Resource):
    
    def __init__(self, gateway, attributes):
        Resource.__init__(self, gateway, attributes)
    
    @staticmethod
    def find(id):
        return Configuration.gateway().action.find(id)
    
    @staticmethod
    def run(id, attributes):
        return Configuration.gateway().action.run(id, attributes)