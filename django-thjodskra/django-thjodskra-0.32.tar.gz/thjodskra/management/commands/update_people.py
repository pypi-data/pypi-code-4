#encoding: utf-8
import sys
from collections import deque
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from ...models import Person

class Command(BaseCommand):

    args = u'<filename>'
    help = u'Updates people from þjóðskrá'

    def handle(self, *args, **options):

		fname = args[0]
		f = open( fname, 'r' )

		count = 1
		ttime = 0
		lines = [ l for l in f.readlines() ]
		total = len( lines )
		print '%i lines to process'%total
		
		f.seek( 0 )
		buff = deque()

		for l in lines:
			s = datetime.now()
			
			p, fresh = Person.update_from_string( l )
			if fresh: buff.append( p )
			else: p.save()
			count += 1
				
			if len(buff) >= 250:
				Person.objects.bulk_create( buff )
				buff = []
				
			d = datetime.now() - s
			ttime += d.total_seconds()
			avg = ttime/count
			
			sys.stdout.write( '\r Saved %7i people. Remain: %.2fs. Per second: %.1f' % ( count, avg*(total-count), 1/avg ) )
			sys.stdout.flush()
		if len(buff)>0:
			Person.objects.bulk_create(buff)
			
		print '\nDone'
