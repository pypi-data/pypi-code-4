#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django_moip.html.forms import MoipHtmlBaseForm 
from django_moip.html.nit.models import MoipNIT


class MoipNITForm(MoipHtmlBaseForm):
    """
    Form used to receive and record MoIP NIT notifications.
    
    (MoIP have no official NIT test tool)
    """
    class Meta:
        model = MoipNIT

