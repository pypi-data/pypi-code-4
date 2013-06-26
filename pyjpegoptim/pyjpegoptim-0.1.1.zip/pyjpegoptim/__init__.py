#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jpegoptim import JpegOptim

__doc__ = 'JpegOptim'
__version__ = '0.1'

__all__ = ['JpegOptim', ]

if __name__ == '__main__':
    t = JpegOptim('/tmp/test.jpg',quality=0)
    print dir(t)
    print JpegOptim.__doc__
    print t.save('/tmp/test_.jpg')
    t.close()
