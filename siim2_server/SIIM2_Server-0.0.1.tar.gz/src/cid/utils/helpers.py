# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM Server is the web server of SIIM's Framework
Copyright (C) 2013 Infometrika Ltda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def get_json_response_base(error=False):
    if not error:
        rv = {
            'result': 'ok'
        }
    else:
        rv = {
            'result': 'error',
            'msg': ''
        }
    return rv


def get_json_response_form_create(*args,**kwargs):
    """
        {

        "callback_id" : "request uuid4",
        "result"      : "{ok o error}",
        "event_id"    : "uuid4", /* entrada opcional" */
        "msg"         : "mensaje de error, si 'result' = 'error'",
        "class"       : "class_name",
        "form" :
            {
            /* dform template */
            },
        "data" :
            {
                "field0" :
                    {
                        "value"   : "**********",
                        "mandatory"  : "True o False", /* entrada opcional, en ausencia : "False" */
                        "editable"   : "True o False", /* entrada opcional, en ausencia : "False" */
                        "options" : ["xx","yy","zz"]   /* entrada opcional */
                    },
                "field1" :
                    {
                        "value"   : "**********",
                        "mandatory"  : "True o False", /* entrada opcional, en ausencia : "False" */
                        "editable"   : "True o False", /* entrada opcional, en ausencia : "False" */
                        "options" : ["xx","yy","zz"]   /* entrada opcional */
                    },
                "field_n" :
                    {
                        "value"   : "**********",
                        "options" : ["xx","yy","zz"]
                    }
            },
        "actions" : ["create", "delete", "edit"],
        "translations" :
             {
                 "key"    : "Llave",
                 "field"  : "Campo",
                 "create" : "Crear",
                 "edit"   : "Editar",
                 "delete" : "Borrar"
             }
        }
    }
    """


