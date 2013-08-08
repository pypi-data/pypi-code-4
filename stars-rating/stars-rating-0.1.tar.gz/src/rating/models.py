### -*- coding: utf-8 -*- ####################################################

from django.db import models
from django.db import connections, DEFAULT_DB_ALIAS

from djangoratings.fields import RatingField

DEFAULT_RANGE = 10

if connections[DEFAULT_DB_ALIAS].settings_dict['ENGINE'] == 'django.db.backends.sqlite3':
    DEFAULT_SQL_SELECT = 'CASE WHEN (%(field_name)s_score = 0 OR %(field_name)s_votes = 0) THEN 0 ELSE 100/%(range)s*%(field_name)s_score/%(field_name)s_votes END'
else:
    DEFAULT_SQL_SELECT = 'CASE WHEN (%(field_name)s_score = 0 OR %(field_name)s_votes = 0) THEN 0 ELSE 100/%(range)s*%(field_name)s_score/%(field_name)s_votes*ln(%(field_name)s_votes) END'


class RatingBase(object):
    
    rating_field_names = ()
    
    @classmethod
    def avarage_rating_annotate(cls, queryset=None, avarage_name='avarage', sql_select=DEFAULT_SQL_SELECT):
        
        if queryset is None:
            queryset = cls.objects.all()
        
        build_param = lambda name: '%s_%s' % (avarage_name, name) if name else avarage_name
        
        select_dict = {}
        for field_name in cls.rating_field_names:
            select_dict[build_param(field_name)] = sql_select % {
                'range': getattr(cls, field_name).range,
                'field_name': field_name,
            }
        
        #if len(cls.rating_field_names) > 1:
        #    select_dict[build_param(None)] = ' + '.join(select_dict.values())
        
        return queryset.extra(select=select_dict)    


class SingleRatingModel(models.Model, RatingBase):
    rating = RatingField(range=DEFAULT_RANGE, allow_anonymous=False, can_change_vote=True)
    
    rating_field_names = ('rating',)
    
    class Meta:
        abstract = True
    

class DoubleRatingModel(SingleRatingModel):
    originality = RatingField(range=DEFAULT_RANGE, allow_anonymous=False, can_change_vote=True)
    
    rating_field_names = SingleRatingModel.rating_field_names + ('originality',)

    class Meta:
        abstract = True
