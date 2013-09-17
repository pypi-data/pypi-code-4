"""
CADD Stat URLs
"""

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'caddstat.views',
    url(r'^$', 'start'),
    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^about/$', 'about', name='about'),

    # Tests
    url(r'^effectsize/$', 'effectsize', name='effectsize'),
    url(r'^friedman/$', 'friedman', name='friedman'),
    url(r'^kappa/$', 'kappa', name='kappa'),
    url(r'^mad/$', 'mad', name='mad'),
    url(r'^mannwhitneyu/$', 'mwu', name='mwu'),
    url(r'^pearson/$', 'pearson', name='pearson'),
    url(r'^tau/$', 'tau', name='tau'),
    url(r'^ttest/$', 'ttest', name='ttest'),

)
