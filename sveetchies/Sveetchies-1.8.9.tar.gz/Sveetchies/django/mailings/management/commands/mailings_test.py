# -*- coding: utf-8 -*-
"""
Commande en ligne d'utilisation de la queue de tâches
"""
import datetime, logging, os
from optparse import OptionValueError, make_option

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand

from django.contrib.auth.models import User

from Sveetchies.django import mailings

mailings.autodiscover()

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--gogo", dest="gogo_mode", default=False, action="store_true", help="Go go gadget, dummy test."),
        #make_option("-d", "--debug", dest="debug", default=False, action="store_true", help="Active debug mode for mails which implement it."),
    )
    help = "Command to test mailings app, don't use it with a real smtp server."

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        gogo_mode = options.get('gogo_mode')
        self.debug = options.get('debug')
        self.verbosity = int(options.get('verbosity'))

        starttime = datetime.datetime.now()
        
        # Lance les actions
        if gogo_mode:
            self.gogo_mode()
        
        endtime = datetime.datetime.now()

    def gogo_mode(self):
        """
        Exécute les tests
        """
        # Test bidon de séléction d'une clé qui n'existe pas dans le registre
        print "="*60
        try:
            mail1 = mailings.site._registry['entry_that_does_not_exist']
        except KeyError:
            print "*", "Attended non existing key [SUCCESS]"
        else:
            print "*", "Attended non existing key [FAIL]"
            
        # Test de lecture du registre
        print "="*60
        for k,v in mailings.site.get_registry().items():
            print "*", "KEY: %s; Object: %s;"%(k, v.__name__)
        
        # Contenu de test
        context = {
            'dummy_var': u'DUMMY VARIABLE IS DUMMY !',
        }
        recipient1 = 'recipient1@localhost'
        recipient2 = 'recipient2@localhost'
        from_email = 'sender@localhost'
        
        ## Test d'instanciation d'un contrôleur passif
        #print "="*60
        #print "Passive controler"
        #dummy = mailings.site.get_controler('DummyTemplate', passive=True, context=context)
        #print "", "- initial_datas:", dummy.get_initial_datas()
        #print "", "- context:", dummy.get_context()
        #print "", "- content:", dummy.get_content()
        #print "", "- Send_single_mail test"
        #dummy.send_single_mail([recipient1, recipient2], from_email)
        #print "", "- Send_separate_mail test"
        #dummy.send_separate_mail([recipient1, recipient2], from_email)

        # Test d'instanciation d'un contrôleur actif
        print "="*60
        print "Active controler"
        dummy = mailings.site.get_controler('DummyTemplate', passive=False, context=context)
        print "", "- initial_datas:", dummy.get_initial_datas()
        print "", "- context:", dummy.get_context()
        print "", "- content:", dummy.get_content()
        print "", "- Send_single_mail with only one email test"
        dummy.send_single_mail(recipient1, from_email)
        print "", "- Send_single_mail with some email test"
        dummy.send_single_mail([recipient1, recipient2], from_email)
        print "", "- Send_separate_mail test"
        dummy.send_separate_mail([recipient1, recipient2], from_email)
