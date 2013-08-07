from django.conf.urls import patterns, url, include
from socketio_server.views import ExecuteTasksView

defaultpatterns = patterns(r'^socket.io/', include("socketio_server.urls"))

urlpatterns = patterns('',
    url(r'^$', ExecuteTasksView.as_view(), name="tasks"),
)
