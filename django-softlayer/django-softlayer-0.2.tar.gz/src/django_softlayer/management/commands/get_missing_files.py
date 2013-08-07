### -*- coding: utf-8 -*- ####################################################
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_app, get_model, FieldDoesNotExist
from django.conf import settings


class Command(BaseCommand):
    '''Calculates similar albums for each album in database'''
    args = ''
    help = 'Returns missing or empty track files from the SoftLayer'
    option_list = BaseCommand.option_list + (
        make_option('--app_model_field',
                    dest='app_model_field',
                    help='String containing dot separated app, model and field name\n Example: myapp.User.file'),
    )


    def handle(self, app_model_field, *args, **options):
        self.index = 1
        tuples = []
        if not app_model_field:
            if hasattr(settings, 'CMD_MISSING_FILES_SETTINGS'):
                app_model_field = settings.CMD_MISSING_FILES_SETTINGS

        if app_model_field:
            if not isinstance(app_model_field, basestring):
                for obj in app_model_field:
                    tuples.append(obj.split('.'))
            else:
                tuples.append(app_model_field.split('.'))
        else:
            raise CommandError('You must specify --app_model_field option. Example: app.Model.field')

        def printTrack(obj, reason):
            print "%s. Instance: %s\n\tID: %s\n\tReason: %s" % \
                  (self.index, unicode(obj), obj.pk, reason)
            self.index += 1

        def get_missing_files(model, field_name):
            print '----------------Searching missing or incomplete %ss in %s:--------------\n' % \
                  (field_name, model.__name__)
            for obj in model.objects.all():
                try:
                    if getattr(obj, field_name).file.size == 0:
                        printTrack(obj, 'Size is 0')
                except:
                    printTrack(obj, 'FILE NOT FOUND')
            print '----------------------------------Done--------------------------------------'

        for _tuple in tuples:
            model = get_model(_tuple[0], _tuple[1])
            field_name = _tuple[2]
            try:
                model._meta.get_field(field_name)
            except FieldDoesNotExist:
                raise CommandError(
                    'There is no field \"%s\" of model \"%s\" in app \"%s\" ' % (_tuple[2], _tuple[1], _tuple[0]))
            get_missing_files(model, field_name)




