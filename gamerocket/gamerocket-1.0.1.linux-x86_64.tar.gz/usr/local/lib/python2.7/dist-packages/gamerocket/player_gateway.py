from gamerocket.result.error_result import ErrorResult
from gamerocket.result.successful_result import SuccessfulResult
from gamerocket.exceptions.not_found_error import NotFoundError
from player import Player

class PlayerGateway(object):
    def __init__(self, gateway):
        self.gateway = gateway
        self.config = gateway.config
    
    def create(self, params={}):
        response = self.config.http().post("/games/" + self.config.apiKey + "/players", params)
        if "player" in response:
            return SuccessfulResult({"player": Player(self.gateway, response['player'])})
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass
    
    def delete(self, player_id, params={}):
        response = self.config.http().delete("/players/" + player_id, params)
        if "status" in response:
            return SuccessfulResult(response)
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass
    
    def find(self, player_id):
        if player_id == None or player_id.strip() == "":
            raise NotFoundError()
        response = self.config.http().get("/players/" + player_id)
        if "player" in response:
            return SuccessfulResult({"player": Player(self.gateway,response["player"])})
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass
        
    def update(self, player_id, params={}):
        response = self.config.http().put("/players/" + player_id, params)
        if "player" in response:
            return SuccessfulResult({"player": Player(self.gateway,response["player"])})
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass