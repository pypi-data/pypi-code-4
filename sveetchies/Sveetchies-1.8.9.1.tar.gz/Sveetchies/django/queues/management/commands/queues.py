# -*- coding: utf-8 -*-
"""
Commande en ligne d'utilisation de la queue de tâches
"""
import datetime, logging, os
from optparse import OptionValueError, make_option

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand

from django.contrib.auth.models import User

from Sveetchies.logger import LoggingInterface
from Sveetchies.django import queues
from Sveetchies.django import mailings

LOGGING_FILENAME = "queue.log"
DEFAULT_QUEUE_CRON_COMMAND = "django-admin.py queues --pythonpath=%s -v 0 %s" % (os.getcwd(), '%s')

queues.autodiscover()
mailings.autodiscover()

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--browse", dest="browse_job_types", default=False, action="store_true", help="Browse all available job types"),
        make_option("--install", dest="install_mode", default=False, action="store_true", help="Print job schedules to append in your crontab"),
        make_option("--job", dest="job_key", type="string", default=None, help="Launch the named job type. Use '--browse' to see all available jobs", metavar="JOBNAME"),
        make_option("-l", "--logging", dest="logMode", default=False, action="store_true", help="Logging activity details into a file '%s'"%LOGGING_FILENAME),
        make_option("-d", "--debug", dest="debug", default=False, action="store_true", help="Active debug mode for jobs which implement it."),
    )
    help = "Command to manage jobs queue"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        job_key = options.get('job_key')
        browse_job_types = options.get('browse_job_types')
        install_mode = options.get('install_mode')
        self.logMode = options.get('logMode')
        self.debug = options.get('debug')
        self.verbosity = int(options.get('verbosity'))

        starttime = datetime.datetime.now()
        
        self.logger = LoggingInterface(passive=True, logging_filename=LOGGING_FILENAME, logger_id='queues-logger', error_blocker=False)
        self.logger.connect_logger(
            output_verbosity=self.verbosity,
            logging_verbosity=int(self.logMode),
        )

        # Lance les actions
        if browse_job_types:
            self.browse_job_types()
        if install_mode:
            self.install()
        if job_key:
            self.do_job(job_key)
        
        endtime = datetime.datetime.now()
        self.logger.info("~~~ Durée : %s" % str(endtime-starttime))

    def install(self):
        """
        Affiche le contenu de programmation à installer dans crontab
        
        La sortie n'utilise pas le logger mais directement un print car cette commande 
        n'est pas faite pour être loggué et que la sortie de terminal de logger 
        comportent de la mise en forme de terminal.
        """
        i = 1
        basecmd = getattr(settings, 'QUEUE_CRON_COMMAND', DEFAULT_QUEUE_CRON_COMMAND)
        print "# BEGIN scheduled queues jobs"
        for k,v in queues.site.get_registry().items():
            job_cmd = basecmd % ("--job="+k)
            if v[1].cron_time:
                print "%s %s" % (v[1].cron_time, job_cmd)
            i += 1
        print "# END scheduled queues jobs"

    def browse_job_types(self):
        """
        Liste les types de jobs disponibles
        """
        i = 1
        queryset = queues.site.get_registry().items()
        if len(queryset)>0:
            self.logger.title(u"Types de jobs disponibles :")
            for k,v in queryset:
                self.logger.info("%s) %s [name=%s]" % (i, v[0], k))
                if v[1].cron_help:
                    self.logger.info(u"Programmation: %s" % v[1].cron_help, indent="   ")
                if v[1].help:
                    self.logger.info(u"Aide: %s" % v[1].help, indent="   ")
                self.logger.info("", log=False, indent="   ")
                i += 1
        else:
            self.logger.title(u"Aucun job enregistré")

    def do_job(self, job_key):
        """
        Exécute le type de job spécifié
        """
        job = queues.site.get_registry().get(job_key, None)
        if not job:
            self.logger.error("Job type '%s' is not registered" % job_key, error_blocker=True)
        j = job[1](self.logger, debug=self.debug)
        j.do()