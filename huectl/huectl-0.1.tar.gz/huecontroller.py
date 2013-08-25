#!/usr/bin/env python

'''
A very simple Philips Hue command line tool and controller class

Based on the phue python library
https://github.com/studioimaginaire/phue

Published under the GWTFPL - http://www.wtfpl.net

"Hue Personal Wireless Lighting" is a trademark owned by Koninklijke Philips
Electronics N.V., see www.meethue.com for more information.

I am in no way affiliated with the Philips organization.
'''

__version__ = '0.1'

import phue as hue
import sys
import os
import json
import argparse
import logging

class HueController(hue.Bridge):
    def __init__(self, ip):
        self.__cfgpath = os.path.expanduser('~/.hue')
        if not os.path.exists(self.__cfgpath):
            os.mkdir(self.__cfgpath)

        hue.Bridge.__init__(self, ip)

    def _light_to_dict(self, light):
        print light
        ldict = { 'id'   : light.light_id,
                  'name' : light.name,
                  'on'   : light.on}

        if light.on is False:
            return ldict

        ldict['brightness'] = light.brightness

        if not hasattr(light, 'colormode'):
            return ldict

        print light
        cm = light.colormode
        ldict['colormode'] = light.colormode
        if cm == u'ct':
            ldict['ct'] = light.colortemp
        elif cm == u'xy':
            ldict['xy'] = light.xy
        elif cm == u'hs':
            ldict['hue'] = light.hue
            ldict['sat'] = light.saturation

        return ldict

    def _set_light(self, cfg):#print cfg
        cmd = { 'on' : cfg['on'] }

        if cfg['on']:
            cmd['bri'] = cfg['brightness']
            if cfg.has_key('colormode'):
                cm = cfg['colormode']
                if cm == 'ct':
                    cmd['ct'] = cfg['ct']
                elif cm == 'xy':
                    cmd['xy'] = cfg['xy']
                elif cm == 'hs':
                    cmd['hue'] = cfg['hue']
                    cmd['sat'] = cfg['saturation']

        self.set_light(cfg['id'], cmd)

    def save_state(self, name):
        lights = bridge.get_light_objects('id')
        state = [ self._light_to_dict(light) for light in self.lights ]
        text = json.dumps(state, sort_keys=True,
                          indent=4, separators=(',', ': '))
        filepath = self._cfgname_to_path(name)
        with open(filepath, 'w') as fd:
            fd.write(text)

    def _cfgname_to_path(self, name):
        filename = '%s.huecfg' % name
        filepath = os.path.join(self.__cfgpath, filename)
        return filepath

    def load_state(self, name):
        filepath = self._cfgname_to_path(name)
        fd = open(filepath, 'r')
        state = json.load(fd)
        for light in state:
            self._set_light(light)

    def lights_off(self):
        self.lights_all_set(False)

    def lights_on(self):
        self.lights_all_set(True)

    def lights_all_set(self, onoff, ttime=None):
        all_lights = hue.AllLights(self)
        all_lights.transitiontime = ttime
        all_lights.on = onoff

    @property
    def configs(self):
        for filepath in os.listdir(self.__cfgpath):
            if filepath.endswith('huecfg'):
                filename = os.path.basename(filepath)
                yield filepath[:-7]

