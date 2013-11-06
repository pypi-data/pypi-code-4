#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Squeezeui - Graphical user interface for Squeezebox players.

import os
from squeezeui import player

def get_actual_filename(name):
    #TODO: make real fix. 
    #HACK lib=Lib on windows. Need to correct case for qml.
    if os.name == 'nt':
        name = name.replace('lib', 'Lib')
    return name

player.config['datapath'] = os.path.split(
    os.path.dirname(os.path.abspath(get_actual_filename(player.__file__))))[0]
    
player.start_blocking_with_audioplayer()
