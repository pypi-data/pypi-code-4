#!/usr/bin/python
# -*- coding: utf-8 -*-
from requests import get

def listarregistros(domain, bases):
    """Função que lista todos os registros ainda não indexados"""
    
    listabases = []
    listaregs = []
    values = {'$$':'{"select":["id_reg"],"filters":[{"field":"dt_index_tex","term":null,"operation":"="}]}'}
    for x in bases:
        url = domain + '/api/reg/' + x['nome_base']
            
        recebe = get(url, params=values)
        json_resp = recebe.json()
        listaregistros = json_resp["results"]
        for y in listaregistros:
            base = x['nome_base']
            reg = y['id_reg']
            listabases.append(base)
            listaregs.append(reg)
    return listabases, listaregs