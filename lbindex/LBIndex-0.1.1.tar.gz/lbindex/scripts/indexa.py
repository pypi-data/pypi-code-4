#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from pyelasticsearch import ElasticSearch
from requests import get, put  
from datetime import datetime

logger = logging.getLogger("LBIndex")

def indexar(domain, elastic, listabases, listaregs):
    """Função que lança os registros no elasticsearch e marca na base a data e hora da indexação"""
    
    es = ElasticSearch(elastic)
    for reg, base in zip(listaregs, listabases):
        urles = elastic + base + '/' + base + '/' + str(reg)
        urlrest = domain + '/api/reg/' + base + '/' + str(reg)
        urlfull = urlrest + '/full'
        
        recebe = get(urlfull)
        jsonfull = recebe.json()
        erro = '_status' in jsonfull and '_error_message' in jsonfull and '_request' in jsonfull and '_path' in jsonfull
        if erro and len(jsonfull) == 4:
            logger.error (urlrest + 'não pode ser indexado - ' + str(jsonfull['_status']) + ': ' + jsonfull['_error_message'])
        else:
            es.index(base,base, jsonfull, id=reg)
            logger.info (urles + ' indexado com sucesso!')
               
            values = {'$method': 'PUT', 'dt_index_tex': str(datetime.now())}
            put(urlrest, data=values)