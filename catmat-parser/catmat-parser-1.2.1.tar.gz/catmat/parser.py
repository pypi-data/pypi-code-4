#coding: utf-8
from xml.etree import ElementTree as ET

class CatmatParser(object):

    def __init__(self, xml_string):
        self.__tree = ET.fromstring(xml_string)
        self.__data = []

    def to_hash(self):
        for item in self.__tree.find('itens').findall('item'):
            hash_data = {}
            unidades = []
            descricao = item.find('descricao').text.strip()
            for unidade in item.find('unidades').findall('unidade'):
                unidades.append([unidade.find('sigla_unidade_fornecimento').text.strip(),
                                 unidade.find('capacidade').text.strip(),
                                 unidade.find('unidade_medida').text.strip()])
            hash_data['descricao'] = descricao
            hash_data['unidades']  = unidades
            self.__data.append(hash_data)
        return self.__data
