from django.db import models
from django.utils import translation
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.base import ModelBase
from django.core.exceptions import FieldError

class LitBaseCurrentManager(models.Manager):
    """
    It's a special manager for LitBase model that filter queryset 
    with current language
    """
    def get_query_set(self):
        litmodel = models.get_model(self.model._meta.app_label,
                                     self.model.LitMeta.litmodel)
        db_table = litmodel._meta.db_table
        select_dict = dict([
                        (field.column,"%s.%s" % (db_table,field.column))
                        for field in litmodel._meta.fields 
                            if field.name not in ['id',
                            self.model.LitMeta.fieldname]
                        ])
        filter_dict = {
            "%s__language__iexact" % \
            self.model.LitMeta.litmodel.lower():translation.get_language()
        }
        qs = super(LitBaseCurrentManager, self).get_query_set()\
            .extra(select=select_dict,tables=('%s' % (db_table),))\
            .filter(**filter_dict)\
                
        if hasattr(self.model.LitMeta,'ordering'):
            return qs.order_by(*self.model.LitMeta.ordering)
        return qs
    
    def _make_kwargs(self,**kwargs):
        litmodel = models.get_model(self.model._meta.app_label,
                                     self.model.LitMeta.litmodel)
        base_kw = {}
        lit_kw = {}
        base_fields = [field.name for field in self.model._meta.fields]
        lit_fields = [field.name for field in litmodel._meta.fields 
                       if field.name not in ['id',
                                             self.model.LitMeta.fieldname]]
        for k,v in kwargs.items():
            f = k
            if '__' in k:
                f = k.split('__')[0]
            if f in base_fields:
                base_kw[k] = v
            elif f in lit_fields:
                lit_kw[k] = v
            else:
                raise FieldError("Cannot resolve keyword %r into field. "
                    "Choices are: %s" % (
                        f,
                        ", ".join(base_fields + lit_fields))
                    )
        return base_kw,lit_kw,litmodel
   
    def filter(self, *args, **kwargs):
        base_kw,lit_kw,litmodel = self._make_kwargs(**kwargs)        
        return self.get_query_set().filter(
                pk__in=litmodel.litobjects.values_list(
                    self.model.LitMeta.fieldname,
                    flat=True
                ).filter(**lit_kw)).filter(*args, **base_kw)
        
    def get(self, *args, **kwargs):
        base_kw = self._make_kwargs(**kwargs)[0]
        return self.filter(*args, **kwargs).get(*args, **base_kw)


    def exclude(self, *args, **kwargs):
        base_kw,lit_kw,litmodel = self._make_kwargs(**kwargs)        
        return self.get_query_set().filter(
                pk__in=litmodel.litobjects.values_list(
                    self.model.LitMeta.fieldname,
                    flat=True
                ).exclude(**lit_kw)).exclude(*args, **base_kw)

    def order_by(self, *args, **kwargs): 
        return self.get_query_set().order_by(*args, **kwargs)

class LitCurrentManager(models.Manager):
    """
    It's the manager for all LitModel model filtering queryset 
    with current language
    """
    def get_query_set(self):
        try:
            return super(self.__class__, self).get_query_set().filter(
                                    language__iexact=translation.get_language()
                                    )
        except:
            return super(self.__class__, self).get_empty_query_set()

class LitOptions(type):
    """
    Options class for LitModelBase.
    """
    class Schema:
        def __getattr__(self, attr):
            t_model = getattr(self, self.LitMeta.tradmodel)
            return getattr(self, attr, getattr(t_model, attr))

class LitModelBase(ModelBase):
    """
    Lit metaclass. This metaclass parses LitOptions.
    """
    def __new__(cls, name, bases, attrs):
        new = super(LitModelBase, cls).__new__(cls, name, bases, attrs)
        lit_opts = attrs.pop('LitMeta', None)
        setattr(new, '_lit_meta', LitOptions(lit_opts))
        return new

class LitBase(models.Model):
    """
    This is an abstract class that defines the base object 
    to globalization of content.
    """
    __metaclass__ = LitModelBase
    litobjects = LitBaseCurrentManager()

    lit_default_unicode = models.CharField(_(u'Lit default unicode'),
                                            max_length=255,
                                            default = "",
                                            blank=True)

    @property
    def lit(self):
        """
        It returns the related LitModel instance with 
        the current language
        """
        try:
            litmodel = models.get_model(self.__class__._meta.app_label,
                                         self.__class__.LitMeta.litmodel)
            kwargs = {
                '%s__pk' % self.__class__.LitMeta.fieldname: self.pk
            }
            return litmodel.litobjects.get(**kwargs)
        except:
            return None
    
    def __unicode__(self):
        if self.lit_default_unicode:
            return self.lit_default_unicode
        else:
            return "%s %s" % (self.__class__.__name__, self.pk)

    class LitMeta:
        """
        This is a class Meta that define which model is the related LitModel 
        and which field in the related model refers to this LitBase model
        """
        litmodel = None  
        # Must be a string that define the LitModel 
        # class name that refers to sel as foreign key
        fieldname = None
        ordering = ()
        
    class Meta:
        abstract = True
 

class LitModel(models.Model):
    """
    This is an abstract class that defines the globalization of content.
    """
    language = models.CharField(verbose_name = _(u"Language"),
                                max_length=40,
                                choices=settings.LANGUAGES,default = settings.LANGUAGE_CODE)
    litobjects = LitCurrentManager()
    
    def __unicode__(self):
        return u"%s (%s)" % (self.__class__.__name__,self.language)
    
    def save(self,*args,**kwargs):
        if self.language == settings.LANGUAGE_CODE:
            for f in self.__class__._meta.fields:
                if f.get_internal_type() == "ForeignKey":
                    if hasattr(f.rel.to,"LitMeta") and \
                    getattr(f.rel.to.LitMeta,"fieldname") == f.name:
                        litbase = getattr(self,f.name)
                        litbase.lit_default_unicode = self.__unicode__()
                        litbase.save()
        super(LitModel,self).save(*args,**kwargs)
    
    class Meta:
        abstract = True