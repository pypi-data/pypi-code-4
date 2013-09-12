from gamerocket.result.error_result import ErrorResult
from gamerocket.result.successful_result import SuccessfulResult
from gamerocket.exceptions.not_found_error import NotFoundError
from achievement import Achievement

class AchievementGateway(object):
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.config = gateway.config
    
    def find(self, player_id, id, attributes):
        if player_id == None or player_id.strip() == "" or id == None or id.strip() == "":
            raise NotFoundError()
        response = self.config.http().get("/players/" + player_id + "achievements/" + id, attributes)
        if "achievement" in response:
            return SuccessfulResult({"achievement": Achievement(self.gateway,response["achievement"])})
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass