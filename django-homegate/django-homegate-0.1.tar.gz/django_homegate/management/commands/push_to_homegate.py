from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model
from django.conf import settings

from homegate.homegate import Homegate

class Command(BaseCommand):
    help = 'Collect all real estate objects and it\'s IDX records to push to Homegate.'

    def handle(self, *args, **options):
        '''
        '''
        proj, app_label, _, class_name = settings.HOMEGATE_REAL_ESTATE_MODEL.split('.')
        RealEstateModel = get_model(app_label, class_name)
        rems = RealEstateModel.objects.ready_to_push()
        objs = []
        for rem in rems:
            objs.append(rem.get_idx_record())
        
        hg = Homegate(settings.HOMEGATE_AGENCY_ID, 
                host=settings.HOMEGATE_HOST, 
                username=settings.HOMEGATE_USERNAME, 
                password=settings.HOMEGATE_PASSWORD)
        hg.push(objs)
        
        for rem in rems:
            rem.published_idx_record()
        
        del hg # good bye
        