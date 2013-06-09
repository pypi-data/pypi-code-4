# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------

import pyojo
from pyojo import server


@pyojo.route("/")
def Home(request):
    return request.module("index.html")


print "Service starts..."
server.main()
