# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

SIIM Models are the data definition of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

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

#system, and standard library

#neomodel primitives
from neomodel.properties import (Property,
                                 DateTimeProperty,
                                 FloatProperty,
                                 IntegerProperty,
                                 StringProperty)

#CaliopeStorage
from odisea.CaliopeStorage import CaliopeNode


class RegistroPredioCatastroTipo2(CaliopeNode):
    #: Unique and indexed properties first
    sector = StringProperty(unique_index=True)
    chip = StringProperty(unique_index=True)
    cedula_catastral = StringProperty(unique_index=True)
    #: All other
    matricula = StringProperty()
    id_lote = StringProperty()
    codigo_direccion = StringProperty()
    direccion_actual = StringProperty()
    escritura = StringProperty()
    notaria = IntegerProperty()
    fecha_documento = DateTimeProperty()
    area_terreno = FloatProperty()
    area_construida = FloatProperty()
    tipo_propiedad = IntegerProperty()
    codigo_destino = IntegerProperty()
    clase_predio = StringProperty()
    codigo_estrato = IntegerProperty()
    zona_fisica_geoeconomica = StringProperty()


class SIIMForm(CaliopeNode):
    def __init__(self, *args, **kwargs):
        super(SIIMForm, self).__init__(*args, **kwargs)

    def get_form_data(self):
        self._get_node_data()

    def set_form_data(self, data):
        return self.evolve(**data)




