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

from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Registry import registerWidget
from AccessControl import ClassSecurityInfo

from Products.SmartColorWidget import LOG

DEC_TO_HEXA = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'a',
    11: 'b',
    12: 'c',
    13: 'd',
    14: 'e',
    15: 'f',
    }


class SmartColorWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro': '@@smartcolorwidget-macros',
        'helper_js': ('++resource++smartcolorwidget-static/smartcolor_helper.js',),
        'helper_css': ('@@smartcolor_helper.css',),
        })

    security = ClassSecurityInfo()

    def decToHexa(self, dec):
        """ convert decimal value to hexadecimal """

        if dec < 0 or dec > 255:
            return 'FF'

        first = dec % 16
        second = (dec / 16) % 16

        first = DEC_TO_HEXA.get(first)
        second = DEC_TO_HEXA.get(second)

        return  second + first


    def getHTMLColorForRGB(self, R, G, B):
        """ """
        R = self.decToHexa(R)
        G = self.decToHexa(G)
        B = self.decToHexa(B)

        return "#" + R + G + B


    def RGB_to_HSL(self, R, G, B):
        """
        convert RGB color to HSL
        SL values = in [0 .. 99]
        H value = in [0 .. 359]
        RGB values = in [0 .. 255]
        """

        return


    def HSL_to_RGB(self, H, S, L):
        """
        convert HSL color to RGB
        SL values = in [0 .. 99]
        H value = in [0 .. 359]
        RGB values = in [0 .. 255]
        """

        H = float(H) / 360
        S = float(S) / 100
        L = float(L) / 100

        if S==0:
           R = L * 255
           G = L * 255
           B = L * 255
        else:
           if L < 0.5 :
               var_2 = L * ( 1 + S )
           else:

               def Hue_2_RGB( v1, v2, vH ):
                   #Function Hue_2_RGB
                   if vH < 0 :
                       vH += 1
                   if vH > 1 :
                       vH -= 1
                   if ( 6 * vH ) < 1 :
                       return ( v1 + ( v2 - v1 ) * 6 * vH )
                   if ( 2 * vH ) < 1 :
                       return ( v2 )
                   if ( 3 * vH ) < 2 :
                       return ( v1 + ( v2 - v1 ) * ( ( 2 / 3 ) - vH ) * 6 )
                   return ( v1 )

               var_2 = ( L + S ) - ( S * L )
               var_1 = 2 * L - var_2
               R = 255 * Hue_2_RGB( var_1, var_2, H + ( 1 / 3 ) )
               G = 255 * Hue_2_RGB( var_1, var_2, H )
               B = 255 * Hue_2_RGB( var_1, var_2, H - ( 1 / 3 ) )

        color = { 'R' : R,
                  'G' : G,
                  'B' : B,}
        return color

registerWidget(SmartColorWidget,
               title='Color',
               description=('Pick a color!'),
               used_for=('Products.Archetypes.public.StringField',)
               )
