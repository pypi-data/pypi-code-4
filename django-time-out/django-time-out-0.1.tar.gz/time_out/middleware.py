# Django/Python imports
from datetime import datetime
from django.shortcuts import render_to_response

# App imports
from .models import MaintenanceSchedule


def get_current_time():
    """
    Determine what the current time.
    :return: Time data object.
    """
    return datetime.now()


class DownTimeMiddleware(object):


    def process_request(self, request):
        """
        Hook: process_request()
        Called on each request, before Django decides which view to execute.
        :param request:
        :return:
        """
        # If the admin then don't show maintenance page.
        if request.path.startswith("/admin"):
            return None

        # Filter all objects
        now = get_current_time()
        objects = MaintenanceSchedule.objects.filter(start_time__lt=now, end_time__gt=now, active=True)

        if objects.count() > 0:
            # If we have more than one.
            maintenance = objects[0]
            if maintenance.maintenancefilter_set.count() > 0:
                for filter in maintenance.maintenancefilter_set.all():
                    if request.path.startswith(filter.path):
                        abort_request = True
                        break
                else:
                    # filters specified, but none matched the request
                    abort_request = False
            else:
                # no filters specified, means we abort the request
                abort_request = True

            if abort_request:
                context = {'maintenance': maintenance}
                return render_to_response('maintenance/downtime.html', context)

        return None




























