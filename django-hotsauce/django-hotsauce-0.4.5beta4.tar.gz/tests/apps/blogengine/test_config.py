#!/usr/bin/env python
from iniparse import INIConfig
cfg = INIConfig(open('development.ini'))
print cfg.authkit.setup_enable
