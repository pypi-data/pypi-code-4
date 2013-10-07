from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^bitbucket/(?P<secret_key>.+)$', 'ftp_deploy.views.Bitbucket', name='ftpdeploy_bitbucket'),
                       )
