from configuration import Configuration
from resource import Resource

class Game(Resource):
    
    def __init__(self, gateway, attributes):
        Resource.__init__(self, gateway, attributes)
    
    @staticmethod
    def find(id):
        return Configuration.gateway().game.find(id)