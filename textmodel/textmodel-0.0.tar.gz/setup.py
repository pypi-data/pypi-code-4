# -*- coding: latin-1 -*-

#!/usr/bin/env python

from distutils.core import setup

setup(name='textmodel',
      version='0.0',
      description= \
          'A datatype holding textual data (textmodel) '\
          'and a text widget (wxtextview) as demosntration. '\
          'Textmodel does not depend on a specific gui-toolkit.',
      author='C. Ecker',
      author_email='christof.ecker@googlemail.com',
      url='',
      packages=['textmodel', 'wxtextview'] 
     )

