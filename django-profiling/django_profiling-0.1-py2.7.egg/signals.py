from logging import getLogger

from django.db.models.signals import pre_delete

from dprofiling.models import Profile



log = getLogger('dprofiling.signals')

def remove_dumps(sender, instance, **kwargs):
    if instance.dump:
        try:
            log.debug('Removing profile dump at %s' % (instance.dump.path,))
            instance.dump.delete(save=False)
        except:
            log.exception('Error removing a profile dump')


pre_delete.connect(remove_dumps, sender=Profile)

