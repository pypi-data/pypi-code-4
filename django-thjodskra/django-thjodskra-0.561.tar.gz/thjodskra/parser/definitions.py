#encoding: utf-8

from .dates import l2d, s2d
	
PERSON = [
	( 'einkenni', 			'type', 			 2, str ),	#Einkenni: FE - Einstaklingar, FF - Fyrirtæki
	( 'nafnnumer', 			'personal_id', 		 8, str ),	#Nafnnúmer
	( 'kennitala', 			'ssn', 				10, str ),	#Kennitala
	( 'fjolskyldunumer',	'family_id', 		10, str ),	#Fjölskyldunúmer
	( 'sort_code', 			'sort_code', 		31, str ),	#Röðunarsvæði fyrir nafn
	( 'logheimili', 		'domicile', 		12, str),	#Lögheimiliskóði
	( 'skip_1', 			'skip_1', 			 3, str ),	#Autt
	( 'kyn', 				'sex', 				 1, str ),	#Kyn
	( 'hjuskaparstada',		'marital_status',	 1, str ),	#Hjúskaparstaða
	( 'skip_2', 			'skip_2', 			 2, str ),	#Autt
	( 'bannmerking',		'blocked', 			 1, str ),	#Bannmerking
	( 'rikisfang', 			'nationality', 		 2, str ),	#Ríkisfang
	( 'faedingarstadur', 	'place_of_birth', 	 4, str ),	#Fæðingastaður
	( 'faedingardagur', 	'date_of_birth', 	 8, l2d ),	#Fæðingadagur
	( 'nafn', 				'name', 			31, str ),	#Nafn
	( 'kennitala_maka', 	'ssn_spouse', 		10, str ),	#Kennitala maka
	( 'logheimili_112', 	'domicile_112', 	12, str ),	#Lögheimiliskóði 1. Des s.l.
	( 'dags_hreyfing', 		'mod_date', 		 6, s2d ),	#Dagsetning hreyfingar
	( 'adsetur', 			'residence', 		12, str ),	#Aðsetur - lögheimiliskóði
	( 'logheimili_sidast',	'domicile_last', 	12, str ),	#Síðasta lögheimili á Íslandi
	( 'kennitala_umbods', 	'ssn_guardian', 	10, str ),	#Kennitala umboðsmanns
	( 'skip_3', 			'skip_3', 			13, str ),	#Autt
	( 'sokn', 				'parish', 			 3, str ),	#Sókn
	( 'postnumer', 			'postcode', 		 3, str ),	#Póstnúmer
	( 'heimilisfang_nf', 	'address', 			21, str ),	#Heimilisfang í nefnifalli
	( 'heimilisfang_thf', 	'address_thf', 		21, str ),	#Heimilisfang í þágufalli
	( 'skip_4', 			'skip_4', 			23, str ),	#Autt
	( 'afdrif',  			'status', 			 4, str ),	#Afdrif
	( 'dags_afdrif', 		'status_date', 		 6, s2d )	#Dagsetning afdrifa
]

ORGANISATION = [
	( 'einkenni', 			'type', 			 2, str ),	#Einkenni: FE - Einstaklingar, FF - Fyrirtæki
	( 'skip_1', 			'skip_1',	 		 8, str ),	#Autt
	( 'kennitala', 			'ssn', 				10, str ),	#Kennitala
	( 'sveitarfelag', 		'province', 		 4, str ),  #Sveitarfélag póstfangs
	( 'postnumer',			'postcode', 		 3, str ),	#Póstnúmer
	( 'gamalt_rekstrarform','old_org_type', 	 1, str ),  #Gamalt rekstrarform
	( 'starfsstadur', 		'location', 		 4, str ),  #Starfsstaður
	( 'sort_code', 			'sort_code', 		31, str ),	#Röðunarsvæði fyrir nafn
	( 'nafn', 				'name', 			31, str ),	#Nafn
	( 'vsk_numer', 			'vat_number', 		10, str ),  #Virðisaukaskattsnúmer
	( 'skip_2',				'skip_2', 			21, str ),  #Autt
	( 'heimilisfang_nf', 	'address', 			21, str ),	#Heimilisfang í nefnifalli
	( 'stjornarformadur',	'chairman_ssn',		10, str ),  #Kennitala stjórnarformanns 
	( 'skip_3', 			'skip_3', 			 8, str ),	#Autt
	( 'dags_hreyfing', 		'mod_date', 		 6, s2d ),	#Dagsetning hreyfingar
	( 'rekstrarform', 		'org_type', 	 	 2, str ),  #Rekstrarform
	( 'skip_4', 			'skip_4', 			 3, str ),	#Autt
	( 'gamalt_vsk_numer', 	'old_vat_number', 	 5, str ),  #Gamalt vsk númer
	( 'logheimili', 		'domicile', 		 4, str ),	#Sveitarfélagsnúmer  lögheimilis
	( 'nyskraning', 		'registration_date', 6, s2d ),	#Nýskráning
	( 'starfsemi', 			'activity', 		16, str ), 	#Starfsemi
	( 'skip_5', 			'skip_5', 			10, str ),	#Autt
	('vidtakandi_kennitala','recipient_ssn', 	10, str ),  #Kennitala viðtakanda
	( 'vidtakandi_nafn',	'recipient_name', 	31, str ),  #Nafn þess sem póstur berist til
	( 'skip_6', 			'skip_6', 			 3, str ),	#Autt
	( 'isat', 				'isat', 			 5, str ), 	#ISAT – kóði)
	( 'skip_7', 			'skip_7', 			 8, str ),	#Autt
	( 'afskrad', 			'deregistered', 	 1, str ),	#E - af skrá
	( 'afskra_tegund', 		'dereg_type',	 	 4, str ),	#Tegund afskráningar
	( 'afskrad_dags', 		'dereg_date', 		 8, l2d ),	#Dagsetning afskráningar
	( 'skip_8', 			'skip_8', 			 5, str ),	#Autt
	( 'bannmerking',		'blocked', 			 1, str ),	#Bannmerking
	( 'skip_9', 			'skip_9', 			 8, str ),	#Autt
]

'''
	Skýringar:
	
		Einkenni:
			FE - Einstaklingur
			FF - Fyrirtæki
			
		Kyn:
			1 - Karlmaður, 18 ára eða eldri
			2 - Kvenmaður, 18 ára eða eldri
			3 - Drengur, 17 ára eða yngri
			4 - Stúlka, 17 ára eða yngri
			
		Hjúskaparstaða:
			1 - Ógift
			3 - Gift eða staðfest samvist
			4 - Ekkill / Ekkja
			5 - Skilin að borð og sæng
			6 - Skilin að lögum
			7 - Hjón ekki í samvistum
			8 - Íslendingur í hjúskap með útlending
			9 - Hjúskaparstaða óupplýst
			0 - Íslendingur búsettur erlendis í hjúskap með útlendingi
			L - Íslendingur með lögheimili á Íslandi í hjúskap með óskráðum útlendingi
			
		Afdrif:
			AFMÐ - Afmáð 
			BRFD - Breytt kennitala og fæðingardagur  
			BRFL - Brottfelling (brottfluttur af landi, oftast útlendingar) 
			BRNF - Breytt nafn 
			BRNN - Breytt nafnnúmer 
			LÉST - látinn 
			Féla - Félagi slitið 
			Firm - félagi slitið; … 
			Fyri - afskráð; félagsslit ; félag lagt niður, hætt starfsemi; … 
			Hags - engin starfsemi; hætt; sameining; samruni; … 
			Hlut - félagsslit, samr; afskráð í hfskrá ; félagi skipt ; starfs.hætt;  
			Lögb - félagi slitið, þrotabú ; afmáð úr fi-skrá; þrotabú eiganda ;  
			LRHG - engin starfsemi; starfsemi hætt; fyrrv. eitthvað; ….. 
			SAMR - Samruni 
			SKIP - Skiptastjóri			
'''