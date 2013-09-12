from gamerocket.result.error_result import ErrorResult
from gamerocket.result.successful_result import SuccessfulResult
from gamerocket.exceptions.not_found_error import NotFoundError
from game import Game

class GameGateway(object):
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.config = gateway.config
    
    def find(self, id):
        if id == None or id.strip() == "":
            raise NotFoundError()
        response = self.config.http().get("/games/" + id)
        if "game" in response:
            return SuccessfulResult({"game": Game(self.gateway,response["game"])})
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass