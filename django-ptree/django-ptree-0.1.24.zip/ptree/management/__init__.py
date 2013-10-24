from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.conf import settings
from django.utils.importlib import import_module
import ptree.settings
from data_exports.models import Format, Export, Column
import data_exports.models
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from django.contrib.auth import models as auth_models
from django.contrib.auth.management import create_superuser
from django.db.models import signals
import ptree.admin

class CreateObjectsCommand(BaseCommand):
    help = "pTree: Populate the database before launching, with Experiment, Treatments, and Participant objects."
    app_label = None # child classes need to fill this in.
    Participant = None
    Match = None
    Treatment = None
    Experiment = None

    option_list = BaseCommand.option_list + (
        make_option('--participants',
            type='int',
            dest='num_participants',
            help='Number of participants to pre-generate'),
    )

    def create_objects(self, num_participants):
        raise NotImplementedError()


    def handle(self, *args, **options):
        num_participants = options['num_participants']
        self.create_objects(num_participants)
        print 'Created objects for {}'.format(self.app_label)

def create_default_superuser(app, created_models, verbosity, **kwargs):
    """
    Creates our default superuser.
    """
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD
    email = getattr(settings, 'ADMIN_EMAIL', '')
    try:
        auth_models.User.objects.get(username=username)
    except auth_models.User.DoesNotExist:
        s = '\n'.join(['Creating default superuser.',
             'Username: {}'.format(username),
             'Email: {}'.format(email)])
        assert auth_models.User.objects.create_superuser(username, email, password)
    else:
        print 'Default superuser already exists.'

if getattr(settings, 'CREATE_DEFAULT_SUPERUSER', False):
    # From http://stackoverflow.com/questions/1466827/:
    # Prevent interactive question about wanting a superuser created.
    # (This code has to go in this otherwise empty "models" module
    # so that it gets processed by the "syncdb" command during
    # database creation.)
    signals.post_syncdb.disconnect(
        create_superuser,
        sender=auth_models,
        dispatch_uid='django.contrib.auth.management.create_superuser'
    )

    # Trigger default superuser creation.
    signals.post_syncdb.connect(
        create_default_superuser,
        sender=auth_models,
        dispatch_uid='common.models.create_testuser'
    )

def create_csv_export_format(sender, **kwargs):
    try:
        Format.objects.get(name = 'CSV')
    except Format.DoesNotExist:
        csv_format = Format(name="CSV",
                            file_ext="csv",
                            mime="text/csv",
                            template="data_exports/ptree_csv.html")
        csv_format.save()

signals.post_syncdb.connect(
    create_csv_export_format,
    sender=data_exports.models,
)

def create_export(self, Model, export_name, fields):
    model_name = '{}: {} (CSV)'.format(self.app_label, export_name)
    csv_format = Format.objects.get(name="CSV")
    export = Export(name = model_name,
                    slug = slugify(model_name),
                    model = Model,
                    export_format = csv_format)
    export.save()

    for i, field in enumerate(fields):
        column = Column(export = export,
                        column = field,
                        label = field,
                        order = i)
        column.save()

def create_export_for_start_urls(app_label):
    participant_content_type = ContentType.objects.get(app_label=app_label, model='participant')
    create_export(participant_content_type,
                       'start URLs',
                       ['start_url'])

def create_export_for_participants(app_label, Participant):
    participant_content_type = ContentType.objects.get(app_label=app_label, model='participant')
    create_export(participant_content_type,
                       'participants',
                       ptree.admin.get_participant_list_display(Participant))

def create_export_for_matches(app_label, Match):
    match_content_type = ContentType.objects.get(app_label=app_label, model='match')
    create_export(match_content_type,
                       'matches',
                       ptree.admin.get_match_list_display(Match))

def create_export_for_payments(app_label):
    participant_content_type = ContentType.objects.get(app_label=app_label, model='participant')
    create_export(participant_content_type,
                       'payments',
                       ['code', 'total_pay'])


def create_all_data_exports(app_label, Experiment, Treatment, Match, Participant):
    create_export_for_matches(app_label, Match)
    create_export_for_participants(app_label, Participant)
    create_export_for_payments(app_label)
    create_export_for_start_urls(app_label)