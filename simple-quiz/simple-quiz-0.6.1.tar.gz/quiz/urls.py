from django.conf.urls.defaults import *

urlpatterns = patterns('quiz.views',
    (r'^$', 'quiz_list'),
    url(r'^sit/(?P<quiz_id>\d+)/$', 'quiz_sit', name='quiz-sit'),
    url(r'^results/(?P<sitting_id>\d+)/$', 'sitting_details', name='sitting-detail'),
)
