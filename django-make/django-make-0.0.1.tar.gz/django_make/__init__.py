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

        err = ''
        for line in p0.stderr:
            err += line.rstrip()+ '\n' 

        if err == '':
            p0.wait()
            return

        # p1 = subprocess.Popen(
        #     ['find'],
        #     stdin=p0.stdout,
        #     stdout=subprocess.PIPE
        # )
        # p2 = subprocess.Popen(
        #     ['grep', '-v', ".py|.pyc"],
        #     stdin=p1.stdout,
        #     stdout=subprocess.PIPE
        # )
        # p3 = subprocess.Popen(
        #     ['xargs', 'touch'],
        #     stdin=p2.stdout,
        #     stdout=subprocess.PIPE
        # )
        # p0.communicate()

        # p1 = subprocess.Popen(
        #     'find | grep -v ".py" | xargs touch',
        #     shell=True,
        #     stdin=p0.stdout,
        #     stdout=subprocess.PIPE
        # )

        p0.wait()

        return HttpResponse(err, content_type='text/plain')