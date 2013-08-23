#encoding: utf-8
import sys
from datetime import datetime
from ftplib import FTP
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ...models import Person

class Command(BaseCommand):

    help = u'Fetches update file'

    def handle(self, *args, **options):
		
		fname = args[0] if len(args)>0 else 'thjodskra_%s.txt'%datetime.now().strftime('%d%m%Y')
		outfile = open( fname, 'wb' )
		
		thjodskra = settings.THJODSKRA
		ftp = FTP( thjodskra['host'] )
		if thjodskra.has_key('username') and thjodskra.has_key('password'):
			ftp.login( thjodskra['username'], thjodskra['password'] )
		ftp.retrbinary( thjodskra['file'], outfile.write )
		ftp.close()
		
		outfile.truncate()
		outfile.close()
		
		sys.stdout.write( fname )