#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from scripts import buscabases
from scripts import buscaregistro
from scripts import indexa

logger = logging.getLogger("LBIndex")

def main(domain, elastic):
    bases = buscabases.listarbases(domain)
    (listabases, listaregs) = buscaregistro.listarregistros(domain, bases)
    if len(listaregs) == 0:
    	logger.info ('Não existem registros para serem indexados')
    else:
    	logger.info (str(len(listaregs)) + ' registros serão indexados')
    	indexa.indexar(domain, elastic, listabases, listaregs)