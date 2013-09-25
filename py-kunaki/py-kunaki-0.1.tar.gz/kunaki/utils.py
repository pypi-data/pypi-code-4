import xml.etree.cElementTree as ET
from .connection import Connection

REQUEST_URL = 'https://Kunaki.com/XMLService.ASP'


class KunakiElement(object):
    """ Base class for Kunaki request elements.
    """
    def get_tree(self):
        """ Used to build ElementTree structure for the request.
        Returns root Element.
        """
        raise NotImplementedError

    def get_xml(self):
        """ Raw XML version of the request structure.
        """
        return ET.tostring(self.get_tree())


class KunakiRequest(KunakiElement):
    """ Base class for Kunaki requests.
    """
    def __init__(self):
        self.conn = Connection(REQUEST_URL)
        self.response = None
        self.success = False
        self.error_msg = ''

    def parse(self, data):
        """ Used to parse raw response to XML.
        Sets success and error_msg as appropriated.
        """
        try:
            self.response = ET.XML(data)
        except SyntaxError:
            # Needed for malformed XML response from Kunaki
            data = data.replace('\r\n<HTML>\r\n<BODY>\r\n', '')
            self.response = ET.XML(data)
        self.success = self.is_success()
        self.error_msg = self.get_error_msg()

    def send(self):
        """ Sends XML request through the connection.
        """
        self.parse(self.conn.send_request(self.get_xml())[1])

    def is_success(self):
        """ Determines if request was successful.
        """
        assert self.response is not None
        ec = self.response.find('ErrorCode')
        return ec.text == '0'

    def get_error_msg(self):
        """ Retrieves request error message.
        """
        assert self.response is not None
        et = self.response.find('ErrorText')
        return et.text

    def get_response_xml(self):
        """ Returns request response as raw XML.
        """
        assert self.response is not None
        return ET.tostring(self.response)
