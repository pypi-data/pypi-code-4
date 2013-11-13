'''
See https://www.usps.com/business/web-tools-apis/Address-Information-v3-2.htm for complete documentation of the API
'''

import urllib, urllib2
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET


def utf8urlencode(data):
    ret = dict()
    for key, value in data.iteritems():
        ret[key] = value.encode('utf8')
    return urllib.urlencode(ret)


def dicttoxml(dictionary, parent, tagname, attributes=None):
    element = ET.SubElement(parent, tagname)
    if attributes: #USPS likes things in a certain order!
        for key in attributes:
            ET.SubElement(element, key).text = dictionary.get(key, '')
    else:
        for key, value in dictionary.iteritems():
            ET.SubElement(element, key).text = value
    return element


def xmltodict(element):
    ret = dict()
    for item in element.getchildren():
        ret[item.tag] = item.text
    return ret


class USPSXMLError(Exception):
    def __init__(self, element):
        self.info = xmltodict(element)
        super(USPSXMLError, self).__init__(self.info['Description'])


class USPSAddressService(object):
    SERVICE_NAME = None
    API = None
    CHILD_XML_NAME = None
    PARAMETERS = None
    
    def __init__(self, url='http://production.shippingapis.com/ShippingAPI.dll'):
        self.url = url

    def submit_xml(self, xml):
        data = {'XML': ET.tostring(xml),
                'API': self.API}
        response = urllib2.urlopen(self.url, utf8urlencode(data))
        root = ET.parse(response).getroot()
        if root.tag == 'Error':
            raise USPSXMLError(root)
        error = root.find('.//Error')
        if error:
            raise USPSXMLError(error)
        return root

    @staticmethod
    def parse_xml(xml):
        items = list()
        for item in xml.getchildren():
            items.append(xmltodict(item))
        return items
    
    def make_xml(self, userid, addresses):
        root = ET.Element(self.SERVICE_NAME + 'Request')
        root.attrib['USERID'] = userid
        index = 0
        for address_dict in addresses:
            address_xml = dicttoxml(address_dict, root, self.CHILD_XML_NAME, self.PARAMETERS)
            address_xml.attrib['ID'] = str(index)
            index += 1
        return root
    
    def execute(self, userid, addresses):
        xml = self.make_xml(userid, addresses)
        return self.parse_xml(self.submit_xml(xml))


class Address(USPSAddressService):
    """ Base Address class.


    Address Formating Information from the USPS.

    FirmName - Name of Business (XYZ Corp.) [Optional]
    Address1 - Apartment or Suite number. [Optional]
    Address2 - Street Address [Required]
    City [Required]
    State - Abbreviation (CO) [Required]
    Zip5 - 5 Digit Zip Code [Required]
    Zip4 - 4 Digit Zip Code [Optional]

    This method will return a dictionary of values back from the USPS API.  The FullZip value
    is computed.

    {'City': 'Loveland', 'Address2': '500 E 3Rd St', 'State': 'CO', 'FullZip': '80537-5773', 'Zip5': '80537', 'Zip4': '5773'}

    To call:

    from usps.addressinformation import *


    address_validation = Address(user_id='YOUR_USER_ID')
    response = address_validation.validate(address1='500 E. third st', city='Loveland', state='CO')

    If an address is invalid (Doesn't exist) will raise USPSXMLError

    """
    SERVICE_NAME = 'AddressValidate'
    CHILD_XML_NAME = 'Address'
    API = 'Verify'
    USER_ID = ''
    PARAMETERS = ['FirmName',
                  'Address1',
                  'Address2',
                  'City',
                  'State',
                  'Zip5',
                  'Zip4',]

    def __init__(self, user_id, *args, **kwargs):
        super(Address, self).__init__(*args, **kwargs)
        self.USER_ID = user_id

    def format_response(self, address_dict):
        """ Format the response with title case.  Ensures
        that the address is "Human Readable"
        """

        if 'Address1' in address_dict:
            address_dict['Address1'] = address_dict['Address1'].title()

        if 'FirmName' in address_dict:
            address_dict['FirmName'] = address_dict['FirmName'].title()

        address_dict['Address2'] = address_dict['Address2'].title()
        address_dict['City'] = address_dict['City'].title()
        address_dict['FullZip'] = "%s-%s" % (address_dict['Zip5'], address_dict['Zip4'])

        return address_dict

    def validate(self, firm_name='', address1='', address2='', city='', state='', zip_5='', zip_4=''):
        """ Validate provides a cleaner more verbose way to call the API.
        Repackages the attributes
        """
        address_dict = {'FirmName': firm_name,
                        'Address1': address1,
                        'Address2': address2,
                        'City': city,
                        'State': state,
                        'Zip5': zip_5,
                        'Zip4': zip_4}

        valid_address = self.execute(self.USER_ID, [address_dict])
        return self.format_response(valid_address[0])


