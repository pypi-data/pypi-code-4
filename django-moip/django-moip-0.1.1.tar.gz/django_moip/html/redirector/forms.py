#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django_moip.html.forms import MoipHtmlBaseForm
from django_moip.html.redirector.models import MoipRedirector


class MoipRedirectorForm(MoipHtmlBaseForm):
    class Meta:
        model = MoipRedirector