#encoding: utf-8

import math
from datetime import datetime

from django.db import models

from .searchable import SearchablePerson, SearchableManager
import parser

SEX_CHOICES = (
	(1,'Karl'), 
	(2,'Kona'), 
	(3,'Drengur'), 
	(4,'Stúlka')
)

MARITAL_CHOICES = (
	('1','Ógift'),
	('3', 'Gift eða staðfest samvist'),
	('4', 'Ekkill / Ekkja'),
	('5', 'Skilin að borð og sæng'),
	('6', 'Skilin að lögum'),
	('7', 'Hjón ekki í samvistum'),
	('8', 'Íslendingur í hjúskap með útlending'),
	('9', 'Hjúskaparstaða óupplýst'),
	('0', 'Íslendingur búsettur erlendis í hjúskap með útlendingi'),
	('L', 'Íslendingur með lögheimili á Íslandi í hjúskap með óskráðum útlendingi')
)


class Entity( models.Model ):

	name = models.CharField( db_index=True, max_length=31 )	#Nafn
	sort_code = models.CharField( max_length=31 )			#Röðunarsvæði fyrir nafn

	ssn = models.CharField( db_index=True, max_length=10, unique=True )	#Kennitala
	
	postcode = models.CharField( max_length=3 )				#Póstnúmer
	address = models.CharField( max_length=21 )				#Heimilisfang í nefnifalli
	
	blocked = models.BooleanField( default=False )			#Bannmerking
	mod_date = models.DateField( blank=True, null=True )	#Dagsetning hreyfingar

	class Meta:
		abstract = True
		
	def __unicode__( self ):
		return u'%s (%s)'%(self.name, self.ssn)

	@classmethod
	def update_from_string( cls, s ):
		"""Parses an individual entity from a national registry row"""
		
		info = parser.parse( s, cls.definition )
		fresh = False
		try:
			p = cls.objects.get( ssn=info['ssn'] )
		except Person.DoesNotExist:
			p = cls( )
			fresh = True

		for k, v in info.items():
			if hasattr( p, k ):
				setattr( p, k, v )
		return p, False

	@classmethod
	def from_string( cls, s ):
		"""Parses an individual entity from a national registry row"""
		info = parser.parse( s, cls.definition )
		if info:
			p = cls( )
			fresh = True
			for k, v in info.items():
				if hasattr( p, k ):
					setattr( p, k, v )
			return p, fresh
		return None, False

	
class Person( Entity ):
	"""docstring for Person"""

	definition = parser.PERSON
	
	personal_id = models.CharField( max_length=8 )			#Nafnnúmer

	ssn_spouse = models.CharField( max_length=10 )			#Kennitala maka
	ssn_guardian = models.CharField( max_length=10 )		#Kennitala umboðsmanns
	family_id = models.CharField( max_length=10 )			#Fjölskyldunúmer

	sex = models.CharField( max_length=1, choices=SEX_CHOICES )	#Kyn
	marital_status = models.CharField( max_length=1, choices=MARITAL_CHOICES) #Hjúskaparstaða

	domicile = models.CharField( max_length=12 )			#Lögheimiliskóði
	domicile_112 = models.CharField( max_length=12 )		#Lögheimiliskóði 1. Des s.l.
	domicile_last = models.CharField( max_length=12 )		#Síðasta lögheimili á Íslandi
	residence = models.CharField( max_length=12 )			#Aðsetur - lögheimiliskóði
	address_thf = models.CharField( max_length=21 )			#Heimilisfang í þágufalli
			
	nationality = models.CharField( max_length=2 )			#Ríkisfang
	place_of_birth = models.CharField( max_length=4 )		#Fæðingastaður
	date_of_birth = models.DateField( )						#Fæðingadagur

	status = models.CharField( max_length=4 )				#Afdrif
	status_date = models.DateField( blank=True, null=True ) #Dagsetning afdrifa
	
	parish = models.CharField( max_length=3)				#Sókn
	
	objects = SearchableManager( SearchablePerson )
	
	@property
	def spouse( self ):
		if self.ssn_spouse:
			return Person.objects.get( ssn=self.ssn_spouse )
		return None
		
	@property
	def guardian( self ):
		if self.ssn_guardian:
			return Person.objects.get( ssn=self.ssn_guardian )
		return None
				
	@property
	def age( self ):
		now = datetime.now()
		delta = now.date() - self.date_of_birth
		return int( math.floor( delta.days/365.25 ) )
		
class Organisation( Entity ):

	definition = parser.ORGANISATION
	
	province = models.CharField( max_length=4, blank=True, null=True )

	old_org_type = models.CharField( max_length=1, blank=True, null=True )
	location = models.CharField( max_length=4, blank=True, null=True )

	vat_number = models.CharField( max_length=10, blank=True, null=True )

	chairman_ssn = models.CharField( max_length=10, blank=True, null=True )

	org_type = models.CharField( max_length=2, blank=True, null=True )

	old_vat_number = models.CharField( max_length=5, blank=True, null=True )
	domicile = models.CharField( max_length=4, blank=True, null=True )
	registration_date = models.DateField( blank=True, null=True )
	activity = models.CharField( max_length=16 )

	recipient_ssn = models.CharField( max_length=10, blank=True, null=True )
	recipient_name = models.CharField( max_length=31, blank=True, null=True )
	isat = models.CharField( max_length=5, blank=True, null=True )

	deregistered = models.CharField( max_length=1, blank=True, null=True )
	dereg_type = models.CharField( max_length=4, blank=True, null=True )
	dereg_date = models.DateField( max_length=8, blank=True, null=True )
	
	@property
	def is_deregistered( self ):
		return self.deregistered == 'E'
		
	@property
	def chairman( self ):
		if self.chairman_ssn:
			return Person.objects.get( ssn=self.chairman_ssn )
		return None
		
	@property
	def recipient( self ):
		if self.recipient_ssn:
			return Person.objects.get( ssn=self.recipient_ssn )
		return None
		
		
		