#encoding: utf-8
import sys
from collections import deque
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
		
		print fname
'''
Sæll aftur, 

fór yfir samninginn sem ég fékk frá Skrifstofu þjóðskrár, 
þar segir að þið megið fá MAN300E32 (þ.e. innheldur m.a. fjölsk.númer, makakennitölu, o.fl).
Fór aðeins í gegnum póstana sem ég hef verið að senda ykkur og mér sýnist ég óvart hafa breytt þessu í einhverju skeytinu í MAN300E34,  en það er önnur skrá sem hefur í sér ríkisfangið og það eigið þið ekki að fá m.v. mín skjöl....
Endilega leiðréttið mig ef það er rangt ! 
-
Þetta breyttist þegar þið bættuð við fyrirtækjaskránni, en hún heitir MAN300F
Flestir sækja frá okkur eina skrá sem inniheldur bæði einstaklinga og fyrirtæki og hún ætti að heita MAN300B32 (en óvart bjó ég til MAN300B34.. sem var rangt að mér sýnist)  

Nú hafið þið leyfi á þessar skrár skv. samningum Þjóðskrár og RSK:
Einstaklingar:
MAN300E32    = Mánaðarlegar breytingar þjóðskrár.
STA300E32       = Heildarskrá tilbúin á hverjum degi ef þarf. 
BRE300E32      = Allar breytingar ársins í einni skrá.

Fyrirtæki:
MAN300F    = Mánaðarlegar breytingar fyrirtækjaskrár
STA300F       = Heildarskrá tilbúin á hverjum degi ef þarf. 
BRE300F      = Allar breytingar ársins í einni skrá.

og ef þið vilijð sækja þetta bara í einni aðgerð,  þá eru einstaklingar og fyrirtæki í þessu:
Einstaklingar+Fyrirtæki:
MAN300B32    = Mánaðarlegar breytingar þjóðskrá+ fyrirtæki
STA300B32       = Heildarskrá tilbúin á hverjum degi ef þarf. 
BRE300B32      = Allar breytingar ársins í einni skrá.

Ef þið sækið núna eina STA300B32 þá fáið þið alla einstaklinga og öll fyrirtæki rétt m.v. daginn í dag.
-
Áskrfitin ykkar m.v. eina heildarskrá í upphafi og svo breytingaskrárnar reglulega.
Venjulega innheimtum við 7.500 kr. þegar STA-skráin er sótt aukalega,  en við skulum hafa hana í boði hússins núna til að fá stofninn ykkar réttan :-)
Svo mynduð þið sækja annað hvort MAN300E32 og MAN300F  EÐA bara MAN300B34 eftir því hvað hentar ykkar forritum betur !
Bestu kveðjur, 
Björn.
'''