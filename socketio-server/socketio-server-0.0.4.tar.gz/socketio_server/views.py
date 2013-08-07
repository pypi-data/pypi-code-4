from django.views.generic.base import View
from django.http import HttpResponse
from socketio_server.models import AsyncTask


class ExecuteTasksView(View):
    
    def get(self, request):
             
        try:
            for task in AsyncTask.objects.filter(finished_on__isnull=True):
                print task
                task.start()
                task.delete()
        except:
            pass

        return HttpResponse("OK")
