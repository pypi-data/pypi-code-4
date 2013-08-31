# -*- coding: utf-8 -*-

# Losely based on django.core.management.commands.runserver and 
# heavily based on django-clientsignal runsocket.

import sys
import os
import logging
from datetime import datetime
from optparse import make_option

from django.conf import settings

from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application

from django.utils import autoreload

import tornado
import tornado.httpserver
import tornado.wsgi

DEFAULT_PORT = "8000"

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--reload', 
            action='store_true',
            dest='use_reloader', 
            default=False,
            help="Use code change auto-reloader"),
        make_option('--static', 
            action='store_true',
            dest='use_static', 
            default=False,
            help="Serve static files"),
        make_option('--multiple', 
            action='store_true',
            dest='use_multiple', 
            default=False,
            help="Use multiple processes (one per CPU core; `--reload` will be ignored)"),
    )
    help = "Starts a Tornado Server."
    args = '[optional port numbers] (listens on multiple ports)'

    requires_model_validation = False

    def handle(self, *ports, **options):
        if settings.DEBUG:
            import logging
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)

        if not ports:
            ports = [DEFAULT_PORT]

        self.ports = ports
        self.run(**options)

    def run(self, **options):
        """
        Runs the server, using the autoreloader if needed
        """
        use_reloader = options.get('use_reloader', False)
        use_multiple = options.get('use_multiple', False)

        if use_reloader and not use_multiple:
            autoreload.main(self.inner_run, (), options)
        else:
            self.inner_run(**options)

    def inner_run(self, **options):
        from django.utils import translation

        shutdown_message = options.get('shutdown_message', '')
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
        
        self.stdout.write("Validating models...\n\n")
        self.validate(display_num_errors=True)
        translation.activate(settings.LANGUAGE_CODE)

        # Run Django from Tornado
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

        base_port = self.ports[0]

        django_handler = get_wsgi_application()

        use_static = options.get('use_static', False)
        if use_static:
            # (r'/static/(.*)', 
            #     tornado.web.StaticFileHandler, 
            #     {'path': static_path}),
            # XXX: Use tornado for this instead of Django?
            from django.contrib.staticfiles.handlers import StaticFilesHandler
            django_handler = StaticFilesHandler(django_handler)
            
        django_container = tornado.wsgi.WSGIContainer(django_handler)
        tornado_urls = [
                (
                    r'.*', 
                    tornado.web.FallbackHandler, 
                    {'fallback': django_container}
                ),
            ]

        try:
            application = tornado.web.Application(tornado_urls)
            server = tornado.httpserver.HTTPServer(application)

            self.stdout.write((
                "%(started_at)s\n"
                "Django version %(version)s, using settings %(settings)r\n"
                "Tornado Server is running on port(s) %(ports)s\n"
                "Quit the server with %(quit_command)s.\n"
            ) % {
                "started_at": datetime.now().strftime('%B %d, %Y - %X'),
                "version": self.get_version(),
                "settings": settings.SETTINGS_MODULE,
                "ports": ", ".join(self.ports),
                "quit_command": quit_command,
            })

            # Add the remainder of ports.
            for port in self.ports:
                server.bind(port)

            # Go multi-process?
            use_multiple = options.get('use_multiple', False)
            if use_multiple:
                try:
                    server.start(0)
                except RuntimeError:
                    self.stderr.write("Unable to run in multiple processes, IOLoop instance has already been initialized.\n")
                    sys.exit(1)
            else:
                server.start(1)

            io_loop = tornado.ioloop.IOLoop.instance()
            io_loop.start()

        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)


