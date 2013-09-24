# -*- coding: UTF-8 -*-
# all objects() from table notes_eventtype:
loader.save(create_notes_eventtype(1,[u'Aktennotiz', u'', u'', u''],u'Alle Notizen/Ereignisse, die keine andere Form haben',u''))
loader.save(create_notes_eventtype(2,[u'Brief', u'', u'', u''],u'Brief an Kunde, Personen, Organisationen',u''))
loader.save(create_notes_eventtype(3,[u'E-Mail', u'', u'', u''],u'E-Mail an Kunde, Personen, Organisationen',u''))
loader.save(create_notes_eventtype(4,[u'Einschreiben', u'', u'', u''],u'Brief, der per Einschreiben an Kunde oder an externe Personen / Dienst verschickt wird',u''))
loader.save(create_notes_eventtype(5,[u'Gespr\xe4ch EXTERN', u'', u'', u''],u'Pers\xf6nliches Gespr\xe4ch au\xdferhalb des \xd6SHZ, wie z.B. Vorstellungsgespr\xe4ch im Betrieb, Auswertungsgespr\xe4ch, gemeinsamer Termin im Arbeitsamt, im Integrationsprojekt, .',u''))
loader.save(create_notes_eventtype(6,[u'Gespr\xe4ch INTERN', u'', u'', u''],u'Pers\xf6nliches Gespr\xe4ch im \xd6SHZ',u''))
loader.save(create_notes_eventtype(7,[u'Hausbesuch', u'', u'', u''],u'Hausbesuch beim Kunden',u''))
loader.save(create_notes_eventtype(8,[u'Kontakt \xd6SHZ intern', u'', u'', u''],u'Kontakte mit Kollegen oder Diensten im \xd6SHZ, z.B. Fallbesprechung mit Allgemeinem Sozialdienst, Energieberatung, Schuldnerberatung, Sekretariat, ...',u''))
loader.save(create_notes_eventtype(9,[u'Telefonat', u'', u'', u''],u'Telefonischer Kontakt mit dem Kunden, anderen Personen, Diensten oder Organisationen ....',u''))
loader.save(create_notes_eventtype(10,[u'Attestation', u'Attestation', u'Bescheinigung', u''],u'',u''))

loader.flush_deferred_objects()
