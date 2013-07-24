from api.sms import Sms
from api.addons import Addons
from api.conference import Conference
from api.cost import Cost
from api.findme import Findme
from api.general import General
from api.group import Group
from api.locator import Locator
from api.numbers import Numbers
from api.recordings import Recordings
from api.registernumbers import Registernumbers
from api.report import Report
from api.routing import Routing
from api.survo import Survo
from api.transcription import Transcription
from api.verifymenow import Verifymenow
from api.voicemail import Voicemail
from api.clicktocall import Clicktocall
from api.clicktofindme import Clicktofindme
from api.clicktofindmelist import Clicktofindmelist
from api.clicktovr import Clicktovr
from api.clicktovoicemail import Clicktovoicemail
from api.clicktosurvo import Clicktosurvo
from api.base import IfbyphoneApiBase

class IfbyphoneClient(object):
    
    def __init__(self, api_key):
        """
        Create an Ifbyphone REST API client
        """
        self.key = api_key
        self.sms = Sms(self)
        self.addons = Addons(self)
        self.conference = Conference(self)
        self.cost = Cost(self)
        self.findme = Findme(self)
        self.general = General(self)
        self.group = Group(self)
        self.locator = Locator(self)
        self.numbers = Numbers(self)
        self.recordings = Recordings(self)
        self.registernumbers = Registernumbers(self)
        self.report = Report(self)
        self.routing = Routing(self)
        self.survo = Survo(self)
        self.transcription = Transcription(self)
        self.verifymenow = Verifymenow(self)
        self.voicemail = Voicemail(self)
        self.clicktocall = Clicktocall(self)
        self.clicktofindme = Clicktofindme(self)
        self.clicktofindmelist = Clicktofindmelist(self)
        self.clicktovr = Clicktovr(self)
        self.clicktovoicemail = Clicktovoicemail(self)
        self.clicktosurvo = Clicktosurvo(self)
        
    def get_key(self):
        """Method for retieving API key
        """
        return self.key