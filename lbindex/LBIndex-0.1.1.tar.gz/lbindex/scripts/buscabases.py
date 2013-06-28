#!/usr/bin/python
# -*- coding: utf-8 -*-
from requests import get


def listarbases(domain):
    """Função que lista todas as bases"""
    
    values = {'$$':'{"select":["nome_base"]}'}
    url = domain + '/api/base'
    
    recebe = get(url, params=values)
    json_resp = recebe.json()
    bases = json_resp["results"]
    return bases