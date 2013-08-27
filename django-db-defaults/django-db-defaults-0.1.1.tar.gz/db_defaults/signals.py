# -*- coding: utf-8 -*-
"""
    db_defaults.signals
    ~~~~~~~~~~~~~~

    This module defines the signals (Observer pattern) sent by
    django-db-defaults.

    Functions can be connected to these signals, and connected
    functions are called whenever a signal is called.

    See :ref:`signals` for more information.

"""

from django.dispatch import Signal

# Sent at the start of the default values sync  of an app
pre_default_sync = Signal(providing_args=["app"])

# Sent after each successful default values sync of an app
post_default_sync = Signal(providing_args=["app"])