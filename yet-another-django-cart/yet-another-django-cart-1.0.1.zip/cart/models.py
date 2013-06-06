from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

class Cart(models.Model):
    creation_date = models.DateTimeField(verbose_name=_('creation date'))
    checked_out = models.BooleanField(default=False, verbose_name=_('checked out'))

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-creation_date',)

    def __unicode__(self):
        return unicode(self.creation_date)

class ItemManager(models.Manager):
    def get(self, *args, **kwargs):
        if 'product' in kwargs:
            kwargs['content_type'] = ContentType.objects.get_for_model(type(kwargs['product']))
            kwargs['object_id'] = kwargs['product'].pk
            del(kwargs['product'])
        return super(ItemManager, self).get(*args, **kwargs)

class Item(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_('cart'))
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=_('unit price'))
    # product as generic relation
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    objects = ItemManager()

    product_options = models.ManyToManyField("ItemOption", blank=True)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('cart',)

    def __unicode__(self):
        return u'%d units of %s' % (self.quantity, self.product.__class__.__name__)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    # product
    def get_product(self):
        return self.content_type.get_object_for_this_type(id=self.object_id)

    def set_product(self, product):
        self.content_type = ContentType.objects.get_for_model(type(product))
        self.object_id = product.pk

    product = property(get_product, set_product)

    # options
    def get_options(self):
        return [o.option for o in self.itemoption_set.all()]

    def set_options(self, options):
        for option in options:
            itemoption = ItemOption(content_type = ContentType.objects.get_for_model(type(option)), object_id = option.pk)
            self.product_options.add(itemoption)

    def clear_options(self):
        return self.product_options.clear()

    options = property(get_options, set_options)


class ItemOption(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    # options
    def get_option(self):
        return self.content_type.get_object_for_this_type(id=self.object_id)

    option = property(get_option)