from danemco.utils.dynamic_import import import_class
from django.db import models
import cPickle
import datetime
import threading
import traceback
import urllib
from django.conf import settings
from django.core.urlresolvers import reverse


class AsyncTask(models.Model):
    sender = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    args = models.TextField(blank=True, null=True)
    kwargs = models.TextField(blank=True, null=True)
    retval = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(blank=True, null=True)
    finished_on = models.DateTimeField(blank=True, null=True)
    servant = models.CharField(max_length=255)
    notify_server = models.BooleanField(default=True)

    class Meta:
        app_label = 'socketio_server'

    def save(self, **kwargs):
        import socketio_settings
        if self.args and type(self.args) == list:
            print self.args, self.kwargs
            self.args = cPickle.dumps(self.args)

        if self.kwargs and type(self.kwargs) == dict:
            self.kwargs = cPickle.dumps(self.kwargs)

        notify = self.notify_server
        self.notify_server = False
        super(AsyncTask, self).save(**kwargs)

        if notify:
            try:
                try:
                    key = settings.KEYFILE
                    https = 's'
                except:
                    https = ''
                file = urllib.urlopen("http%s://%s:%s%s" % (
                    https,
                    socketio_settings.HOST,
                    socketio_settings.PORT,
                    reverse("io:tasks")
                ))
                print "server notified:", file.read()
                file.close()
            except:
                pass

    def start(self):
        self.servant = threading.current_thread().getName()
        self.started_on = datetime.datetime.now()
        self.save()

        try:
            klass = import_class(self.module)
#            if settings.DEBUG:
#                try:
#                    reload(klass.__module__)
#                    klass = import_class(self.module)
#                except Exception, ex:
#                    pass #print ex

            if self.args:
                args = cPickle.loads(str(self.args))
            else:
                args = []

            if self.kwargs:
                kwargs = cPickle.loads(str(self.kwargs))
            else:
                kwargs = {}

            self.retval = klass(*args, **kwargs)
        except:
            self.retval = traceback.format_exc()
            print "error", self.retval

        self.finished_on = datetime.datetime.now()
        self.save()
