from django.db import models
from django.utils.translation import gettext_lazy as _


class Sortable(models.Model):
    # Make instances reorderable
    weight = models.IntegerField(_('weight'), default=0)

    def save(self, *args, **kwargs):
        model = self.__class__
        if self.weight is None:
            try:
                last = model.objects.order_by('-weight')[0]
                self.weight = last.weight + 1
            except IndexError:
                self.weight = 0
        return super(Sortable, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ('weight',)
