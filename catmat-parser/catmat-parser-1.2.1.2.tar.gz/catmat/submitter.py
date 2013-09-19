# coding: utf-8
from xml.etree import ElementTree as ET
from catmat.parser import CatmatParser
from os.path import join, abspath, dirname
import requests

ROOT_PATH = join(abspath(dirname(__file__)))
print ROOT_PATH

class Submitter(object):

    def __init__(self, cpf=1, password=1):
        url = "http://www.comprasnet.gov.br/XML"
        self.production_url = join(url, "producao/consultamatserv.asp")
        self.development_url = join(url, "treinamento/consultamatserv.asp")
        self.__input_xml_path = join(ROOT_PATH, 'input_template.xml')
        tree = ET.parse(self.__input_xml_path)
        self.__cpf = cpf
        self.__password = password
        self.__root = tree
        self.__data = []

    def _get_xml_input_string(self, radical1, radical2='', radical3=''):
        return open(self.__input_xml_path, 'rw').read() %(self.__cpf, self.__password, 
                                                          radical1, radical2, radical3)

    def post_xml(self, radical1, radical2='', radical3=''):
        input_xml = self._get_xml_input_string(radical1, radical2, radical3)
        param_data = {'xml': input_xml}
        
        output_xml = requests.post(self.development_url, data=param_data)
        output_xml_string = output_xml.text.encode('utf-8')
        parser = CatmatParser(output_xml_string)

        return parser.to_hash()
