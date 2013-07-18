# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2012/11/20
# copy: (C) Copyright 2012 Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import sys, os, yaml
from optparse import OptionParser

from .manager import Manager, FileProvider
from .sender import Sender

#------------------------------------------------------------------------------
def main():

  cmdparser = OptionParser(usage='%prog [options] RECIPIENT ... (--help for details)',
                           )

  cmdparser.add_option('-v', '--verbose',
                       dest='verbose', default=0, action='count',
                       help='enable verbose output to STDERR (multiple invocations'
                       ' increase verbosity)')

  cmdparser.add_option('-t', '--template', metavar='FILENAME',
                       dest='template', default=None, action='store',
                       help='set the email template')

  cmdparser.add_option('-s', '--set-variable', metavar='NAME=VALUE',
                       dest='variables', default=[], action='append',
                       help='set additional variables to the template')

  cmdparser.add_option('-y', '--set-variable-yaml', metavar='NAME=YAML',
                       dest='yamls', default=[], action='append',
                       help='identical to --set-variable, except the value is first passed'
                       ' through a YAML parser')

  cmdparser.add_option('-e', '--add-environment',
                       dest='environ', default=False, action='store_true',
                       help='add all environment variables as template variables')

  cmdparser.add_option('--text',
                       dest='text', default=False, action='store_true',
                       help='send text-only email')

  cmdparser.add_option('--html',
                       dest='html', default=False, action='store_true',
                       help='send html-only email')

  cmdparser.add_option('--raw-html',
                       dest='rawHtml', default=False, action='store_true',
                       help='print out the raw HTML email content')

  cmdparser.add_option('-a', '--all',
                       dest='all', default=False, action='store_true',
                       help='send three emails: text-only, html-only and'
                       ' combined text and html versions')

  cmdparser.add_option('-H', '--smtp-host', metavar='HOST',
                       dest='smtpHost', default=None, action='store',
                       help='set the SMTP host machine to connect to')

  cmdparser.add_option('-P', '--smtp-port', metavar='PORT',
                       dest='smtpPort', default=None, action='store',
                       help='set the SMTP port machine to connect to')

  cmdparser.add_option('-f', '--from', metavar='EADDR',
                       dest='fromAddr', default='noreply@localhost', action='store',
                       help='set the from address (default: %default)')

  cmdparser.add_option('-n', '--no-send',
                       dest='nosend', default=False, action='store_true',
                       help='if specified, the email will not actually be sent'
                       ' but will instead be printed to STDOUT')

  #----------------------------------------------------------------------------
  # process the arguments

  (options, args) = cmdparser.parse_args()

  if options.template is None:
    # TODO: perhaps use STDIN?...
    cmdparser.error('a template is required')

  sender = None
  if options.nosend:
    class NoSender(Sender):
      def send(self, mailfrom, recipients, data):
        print >>sys.stdout, '[  ] mail from:', mailfrom
        print >>sys.stdout, '[  ] recipients:', ', '.join(recipients)
        print >>sys.stdout, '[  ] data:'
        print >>sys.stdout, data
    sender = NoSender()

  prov = FileProvider(os.path.dirname(options.template), os.path.basename(options.template))
  eml  = Manager(sender=sender, provider=prov).newEmail()

  if options.fromAddr is not None:
    eml.setHeader('From', options.fromAddr)

  if options.smtpHost is not None:
    eml.manager.sender.smtpHost = options.smtpHost

  if options.smtpPort is not None:
    eml.manager.sender.smtpPort = options.smtpPort

  if options.environ:
    for k, v in os.environ.items():
      eml[k] = v

  if len(options.variables) > 0:
    for k, v in [v.split('=',1) for v in options.variables]:
      eml[k] = v

  if len(options.yamls) > 0:
    for k, v in [v.split('=',1) for v in options.yamls]:
      eml[k] = yaml.load(v)

  count = 0
  if options.text:    count += 1
  if options.html:    count += 1
  if options.all:     count += 1
  if options.rawHtml: count += 1

  if count > 1:
    cmdparser.error('only one of --text, --html, --all and --raw-html can be used at once')

  if count == 0:
    if options.verbose:
      print >>sys.stderr, '[  ] sending email'
    eml.send(recipients=args)

  if options.all:
    if options.verbose:
      print >>sys.stderr, '[  ] sending combined email'
    eml.send(recipients=args)

  if options.all or options.html:
    if options.verbose:
      print >>sys.stderr, '[  ] sending html-only email'
    eml.include = [i for i in eml.include if i != 'text']
    eml.send(recipients=args)

  if options.all or options.text:
    if options.verbose:
      print >>sys.stderr, '[  ] sending text-only email'
    eml.include = ['text']
    eml.send(recipients=args)

  if options.rawHtml:
    sys.stdout.write(eml.getHtml())

  return 0

#------------------------------------------------------------------------------
if __name__ == '__main__':
  sys.exit(main())

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
