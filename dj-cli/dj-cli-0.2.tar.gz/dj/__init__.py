#!/usr/bin/python

"""
    DJ is a wrapper for django-admin.py
"""

import os

import dj.settings
import dj.utils
import dj.context

ctx = dj.context.Context()


def add_packages(packages):
    settings_file = os.path.join(ctx.root, ctx.name, ctx.name, 'settings.py')
    dj.settings.add_packages(settings_file, packages)


def main(args):
    if not len(args):
        dj.utils.print_usage()

    elif args[0] == 'new':
        ctx.update('./' + args[1], args[1])

        data = {
            'name': ctx.name,
            'root': ctx.root,
        }

        script = """
        virtualenv %(name)s
        cd %(name)s/
        source bin/activate
        pip install Django south
        django-admin.py startproject %(name)s
        """ % data

        os.system(script)

        add_packages(['south'])

        script = """
        cd %(name)s/
        source bin/activate
        cd %(name)s/
        python manage.py syncdb -v 0
        """ % data
        os.system(script)

    elif args[0] == 'install':
        data = {
            'name': ctx.name,
            'root': ctx.root,
            'packages': ' '.join(args[1:])
        }

        script = """
        cd %(root)s/%(name)s/
        source %(root)s/bin/activate
        pip install %(packages)s
        """ % data

        os.system(script)

    elif args[0] == 'app':
        app = args[1]

        data = {
            'app': app,
            'root': ctx.root,
            'name': ctx.name,
        }

        script = """
        cd %(root)s/%(name)s/
        source  %(root)s/bin/activate
        python manage.py startapp %(app)s
        """ % data

        os.system(script)

        add_packages([app])

        script = """
        cd %(root)s/%(name)s/
        source  %(root)s/bin/activate
        python manage.py schemamigration %(app)s --initial
        python manage.py migrate %(app)s
        """ % data
        os.system(script)

    elif args[0] == 'run':
        data = {
            'name': ctx.name,
            'root': ctx.root
        }

        script = """
        cd %(root)s/%(name)s/
        source %(root)s/bin/activate
        python manage.py runserver
        # gunicorn %(name)s.wsgi:application
        """ % data

        os.system(script)

    elif args[0] == 'sync':
        app = args[1]

        data = {
            'app': app,
            'name': ctx.name,
            'root': ctx.root
        }

        script = """
        cd %(root)s/%(name)s/
        source %(root)s/bin/activate
        python manage.py schemamigration %(app)s --auto
        python manage.py migrate %(app)s
        """ % data

        os.system(script)

    elif args[0] == 'shell':
        data = {
            'name': ctx.name,
            'root': ctx.root
        }

        script = """
        cd %(root)s/%(name)s/
        source %(root)s/bin/activate
        python manage.py shell
        """ % data

        os.system(script)
