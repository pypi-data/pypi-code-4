#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A nose plugin for annotating failure and logged tracebacks using the
Zope/Paste/WebError conventions.

"""
# NOTE: Not importing unicode_literals under py2, we need native strings.
from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"


import nose.plugins

class NoseTracebackInfoPlugin(nose.plugins.Plugin):
	"""
	Format logged and failure tracebacks using the Zope formatter, thus
	capturing additional information.
	"""

	name = 'traceback-info'
	score = 1000

	enabled = True # Enabled by default
	enable_logcapture = True
	with_filenames = True

	def options(self, parser, env):
		# Match defaults
		if 'NOSE_WITH_TRACEBACK_INFO' not in env:
			env['NOSE_WITH_TRACEBACK_INFO'] = str(self.enabled)

		super(NoseTracebackInfoPlugin,self).options(parser, env)

		parser.add_option(
			"--nowith-traceback-info",
			action="store_false",
			dest=self.enableOpt,
			help="Disable plugin" )
		parser.add_option(
			"--traceback-long-filenames",
			action='store_true',
			dest='traceback_with_filenames',
			default=False,
			help="Use complete filenames, not module names, in formatted tracebacks" )
		parser.add_option(
			'--traceback-nologcapture',
			action='store_false',
			dest='traceback_enable_logcapture',
			default=True,
			help="Do not format tracebacks captured in logs" )

	def configure(self, options, conf):
		super(NoseTracebackInfoPlugin,self).configure(options,conf)
		if not self.enabled: # pragma: no cover
			return
		self.with_filenames = getattr(options, 'traceback_with_filenames', self.with_filenames)
		self.enable_logcapture = getattr(options, 'traceback_enable_logcapture', self.enable_logcapture)
		if self.enable_logcapture:
			# Force the logcapture plugin, enabled by default,
			# to use the zope exception formatter.
			import zope.exceptions.log
			import logging
			logging.Formatter = zope.exceptions.log.Formatter

	def formatError(self, test, exc_info):
		t, v, tb = exc_info
		from zope.exceptions.exceptionformatter import format_exception

		# Omitting filenames makes things shorter
		# and generally more readable, but when the last part of the traceback
		# is in initializing a module, then the filename is the only discriminator

		# Note that we are joining with a native string, not a unicode string. Under
		# python2, tracebacks are byte strings and mixing unicode at this level may
		# result in UnicodeDecodeError, but under python3 tracebacks are unicode
		formatted_tb = ''.join(format_exception(t, v, tb, with_filenames=self.with_filenames))
		if 'Module None' in formatted_tb:
			formatted_tb = ''.join(format_exception(t, v, tb, with_filenames=True))
		# Returning none for the traceback is what lets us trump
		# the earlier plugins. Otherwise we end up with
		# multiple copies
		return (t, formatted_tb, None)

	def formatFailure(self, test, exc_info):
		return self.formatError(test, exc_info)
