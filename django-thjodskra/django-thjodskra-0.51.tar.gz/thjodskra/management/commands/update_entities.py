#encoding: utf-8
import sys
from collections import deque
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Organisation

ENTITIES = {
	'FE': (Person, deque()),
	'FF': (Organisation, deque())
}

class Command(BaseCommand):

    args = u'<filename>'
    help = u'Updates entities from þjóðskrá'

    def handle(self, *args, **options):

		fname = args[0]
		f = open( fname, 'r' )

		count = 0
		updated = 0
		ttime = 0
		lines = [ l for l in f.readlines() ]
		total = len( lines )
 		sys.stdout.write( '%i lines to process\n'%total )
		
		f.seek( 0 )


		for l in lines:
			s = datetime.now()

			t = l[:2]
			klass, buff = ENTITIES.get( t, (None,None) )
			if klass is not None:
				p, fresh = klass.update_from_string( l )
				if p is not None and fresh: buff.append( p )
				elif p is not None:
					p.save()
					updated += 1
				count += 1
				
				if len(buff) >= 250:
					klass.objects.bulk_create( buff )
					ENTITIES[t][1].clear()
				
				d = datetime.now() - s
				ttime += d.total_seconds()
				avg = ttime/(count+1)
			
				sys.stdout.write( '\r Created %7i entities, updated %7i. Remain: %.2fs. Per second: %.1f' % ( (count-updated), updated, avg*(total-count), 1/avg ) )
				sys.stdout.flush()

		#Empty out the remaining items in the buffers
		for klass, buff in ENTITIES.values():
			if len(buff)>0:
				klass.objects.bulk_create(buff)
			
		sys.stdout.write( '\nDone. %i entities updated'%updated )
