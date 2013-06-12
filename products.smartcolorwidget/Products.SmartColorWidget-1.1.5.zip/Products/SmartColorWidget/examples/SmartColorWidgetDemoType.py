## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from Products.Archetypes.public import *
from Products.SmartColorWidget.Widget import SmartColorWidget

schema = BaseSchema +  Schema((
    StringField('color',
                default='#00FFFF',
                searchable=0,
                required=0,
                widget=SmartColorWidget(
		    label='Color',
                    )
               ),
    StringField('color_2',
                default='#00AAFF',
                searchable=0,
                required=0,
                widget=SmartColorWidget(
            label='Color 2',
                    )
               ),

    ))

class SmartColorWidgetDemoType(BaseContent):
    """Demo type for SmartColorWidget """

    content_icon = "document_icon.gif"
    schema = schema

registerType(SmartColorWidgetDemoType)

