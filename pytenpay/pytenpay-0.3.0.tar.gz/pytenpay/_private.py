#!/usr/bin/env python
#coding:utf-8
from os.path import join
from os import getcwd
class TENPAY:
    CERT = join(getcwd(), "tenpay.pem")
    SP_ID = 1215995301
    SP_KEY = '0317e233a9b1b5836ed5c211cf80d15d'
    OP_USER = '1215995301'
    OP_PASSWORD = "tenpaykanrss42qu"


if __name__ == '__main__':
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')





