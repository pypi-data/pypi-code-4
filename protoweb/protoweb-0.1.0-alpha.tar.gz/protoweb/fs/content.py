# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

import os


def read_file(file, flag='r'):
    if not os.path.isfile(file):
        return
    f = open(file, flag)
    content = f.read()
    f.close()
    return content
