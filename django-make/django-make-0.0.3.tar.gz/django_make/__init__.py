import os
import subprocess
from django.conf import settings
from django.http import HttpResponse

class Make(object):

    def process_request(self, req):

        STAGE_ENV_VAR = getattr(settings, 'STAGE_ENV_VAR', 'STAGE')
        STAGE = os.environ.get(STAGE_ENV_VAR, None)
        if not STAGE or STAGE != 'development':
            return
        
        p0 = subprocess.Popen(
            ['make'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        out = ''
        err = ''

        for line in p0.stdout:
            out += line.rstrip()+ '\n' 

        for line in p0.stderr:
            err += line.rstrip()+ '\n' 

        p0.wait()

        if err.strip() == '':
            return

        return HttpResponse(out + err, content_type='text/plain')