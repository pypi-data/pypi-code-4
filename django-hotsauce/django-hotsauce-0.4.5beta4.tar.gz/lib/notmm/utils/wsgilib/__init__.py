#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2010 Etienne Robillard <robillard.etienne@gmail.com>
# All rights reserved.
#
# This file is part of the notmm project.
# More informations @ http://gthc.org/projects/notmm/
"""Mostly Random WSGI Utilities.

Useful for learning and education purposes only. Deploy
in production at your own risks... ;-)
"""

from response import *
from request  import HTTPRequest
from exc      import HTTPClientError, HTTPServerError, HTTPException
