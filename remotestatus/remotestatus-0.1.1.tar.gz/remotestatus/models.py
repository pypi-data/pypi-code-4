import json

from django.core.urlresolvers import reverse
from django.db import models


class CallRound(models.Model):
    """
    An internal incremeneting id to store 'rounds' of status calls to
    remote boxes. Allows us to group a 'round' of calls by a unique id.
    """
    date_checked = models.DateTimeField()

    def __unicode__(self):
        return '%d - %s' % (self.id, self.date_checked.strftime('%m/%d/%Y - %H:%M %p'))

class RemoteBoxModel(models.Model):
    " Normalizes each remote box by `nickname`. "
    nickname = models.CharField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('rs-remote-box-detail', args=[self.id])

class StatusHistory(models.Model):
    " Stores status updates for each remote box in the project's config. "
    call_round = models.ForeignKey(CallRound)
    remote_box = models.ForeignKey(RemoteBoxModel)
    description = models.TextField(null=True, blank=True)
    box_status = models.BooleanField(default=False)
    processes_output = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return 'Round: %d - %s [%s]' % (self.call_round.id, self.nickname, self.box_status and 'UP' or 'DOWN')

    @property
    def processes_display(self):
        d = json.loads(self.processes_output)
        return '<br />'.join([('`%s`: %s' % (i[0], i[1] and 'UP' or 'DOWN')) for i in d.iteritems()])
