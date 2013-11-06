#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Squeezeui - Graphical user interface for Squeezebox players.

import os
import sys
from squeezeui import player

player.config['datapath'] = os.path.dirname(os.path.abspath(sys.argv[0]))

player.start_blocking()
