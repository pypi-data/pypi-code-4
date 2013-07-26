# -*- coding: utf-8 -*-
"""
Réponse HTTP en JSON
"""
import json

from django.http import HttpResponse

class JSONResponse(HttpResponse):
    """
    Surcharge de l'objet ``django.http.HttpResponse`` pour renvoyer un backend JSON
    """
    def __init__(self, obj, nocache=True, indent=None):
        self.original_obj = obj
        self._json_indent = indent
        super(JSONResponse,self).__init__(self.serialize_to_json(obj))
        self["Content-Type"] = "application/json; charset=utf-8"
        if nocache:
            self['Pragma'] = "no-cache"
            self['Cache-Control'] = "no-cache, must-revalidate, max-age=0"

    def serialize_to_json(self, obj):
        return json.dumps(obj, ensure_ascii=False, indent=self._json_indent)
