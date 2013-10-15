from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from data_exports.models import Format, Export, Column
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify


class CreateObjectsCommand(BaseCommand):
    help = "pTree: Populate the database before launching, with Experiment, Treatments, and Participant objects."
    app_label = None # child classes need to fill this in.

    option_list = BaseCommand.option_list + (
        make_option('--participants',
            type='int',
            dest='num_participants',
            help='Number of participants to pre-generate'),
    )

    def create_objects(self, num_participants):
        raise NotImplementedError()

    def create_export_for_start_urls(self):
        # add this export format to the given models.
        model_name = '{}: start URLs (CSV)'.format(self.app_label)
        csv_format = Format.objects.get(name="CSV")
        export = Export(name = model_name,
                        slug = slugify(model_name),
                        model = ContentType.objects.get(app_label=self.app_label, model='participant'),
                        export_format = csv_format)
        export.save()

        column = Column(export = export,
                        column = 'start_url',
                        label = 'start_url',
                        order = 0)
        column.save()

    def create_export_for_payments(self):
        # add this export format to the given models.
        model_name = '{}: payments (CSV)'.format(self.app_label)
        csv_format = Format.objects.get(name="CSV")
        export = Export(name = model_name,
                        slug = slugify(model_name),
                        model = ContentType.objects.get(app_label=self.app_label, model='participant'),
                        export_format = csv_format)
        export.save()

        column = Column(export = export,
                        column = 'code',
                        label = 'code',
                        order = 0)
        column.save()

        column = Column(export = export,
                        column = 'total_pay',
                        label = 'total_pay',
                        order = 1)
        column.save()


    def handle(self, *args, **options):
        num_participants = options['num_participants']
        self.create_objects(num_participants)
        self.create_export_for_start_urls()
        self.create_export_for_payments()
        print 'Created objects for {}'.format(self.app_label)