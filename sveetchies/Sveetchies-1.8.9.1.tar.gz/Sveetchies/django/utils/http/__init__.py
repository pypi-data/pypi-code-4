# -*- coding: utf-8 -*-
"""
Utilitaires HTTP
"""
class Http403(Exception):
    """
    L'usage de cette exception requiert l'installation du middleware associé 
    Http403Middleware, sinon l'effet sera une erreur 500 (vu que l'exception 403 ne sera 
    pas retenue par le middleware mais comme une erreur lambda) et non 403 comme souhaité
    """
    pass 