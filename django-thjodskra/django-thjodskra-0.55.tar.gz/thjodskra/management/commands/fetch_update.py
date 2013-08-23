#encoding: utf-8
import os, sys

from datetime import datetime
from ftplib import FTP
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ...models import Person
	
class Command(BaseCommand):

	help = u'Fetches update file'
	settings = settings.THJODSKRA
	
	def handle(self, *args, **options):
		
		outfile = self.get_file( args[0] if len(args)>0 else None )
		ftp = self.get_ftp_connection()
		
		lines = []
		ftp.retrlines( 'RETR %s'%self.settings['file'], lines.append )
		ftp.close()
		
		outfile.writelines( ['%s\n'%l for l in lines])
		outfile.truncate()
		
		fname = os.path.abspath( outfile.name )
		sys.stdout.write( fname )
		outfile.close()

	def get_file( self, fname ):
		if fname is None:
			fname = self.settings.get( 'outfile', 'thjodskra_%s.txt' )%datetime.now().strftime('%d%m%Y')
		return open( fname, 'w' )
		
	def get_ftp_connection( self ):
		ftp = FTP( )
		ftp.set_pasv( False )
		ftp.connect( self.settings['host'] )
		if self.settings.has_key('username') and self.settings.has_key('password'):
			ftp.login( self.settings['username'], self.settings['password'] )
		return ftp
