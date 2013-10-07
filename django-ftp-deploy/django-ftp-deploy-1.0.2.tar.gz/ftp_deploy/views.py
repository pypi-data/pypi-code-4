# -*- coding: utf-8 -*-

import os
import StringIO
import pycurl
import json
from ftplib import FTP
import certifi

from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from .models import Log
from .conf import *
from .utils import ftp_makedirs


@csrf_exempt
def Bitbucket(request, secret_key):
    """
    View response to bitbucket POST request
    """
    if secret_key != DEPLOY_SECRET_KEY:
        raise Http404

    if request.method == 'POST':

        # BitBucket Settings
        bitbucket_username = BITBUCKET_SETTINGS['username']
        bitbucket_password = BITBUCKET_SETTINGS['password']
        bitbucket_branch = BITBUCKET_SETTINGS['branch']

        # FTP Settings
        ftp_host = FTP_SETTINGS['host']
        ftp_username = FTP_SETTINGS['username']
        ftp_password = FTP_SETTINGS['password']
        ftp_path = FTP_SETTINGS['path']

        json_string = request.POST['payload'].decode('string_escape').replace('\n', '')
        data = json.loads(json_string)

        uri = data['repository']['absolute_url']
        last_commit = len(data['commits']) - 1

        if data['commits'][last_commit]['branch'] == bitbucket_branch:

            try:
                ftp = FTP(ftp_host, ftp_username, ftp_password)
            except Exception, e:
                Log.objects.create(user='FTP Connection', message=e, passed=False)
            else:
                for commit in data['commits']:
                    node = commit['node']
                    files = commit['files']
                    author = commit['author']
                    commit_msg = commit['message']
                    
                    try:    
                        for file_ in files:
                            path = file_['file']
                            if file_['type'] == 'removed':
                                ftp.delete(ftp_path + path.encode('ascii', 'ignore'))
                            else:
                                url = 'https://api.bitbucket.org/1.0/repositories%sraw/%s/%s' % (uri, node, path)
                                url = str(url.encode('utf-8'))

                                dirname = os.path.dirname(path)
                                ftp_makedirs(ftp, ftp_path, dirname)
                                
                                b = StringIO.StringIO()
                                curl = pycurl.Curl()
                                curl.setopt(pycurl.CAINFO, certifi.where())
                                curl.setopt(curl.USERPWD, '%s:%s' % (bitbucket_username, bitbucket_password))
                                curl.setopt(curl.URL, url)
                                curl.setopt(curl.WRITEFUNCTION, b.write)
                                curl.perform()
                                local_file = open(ftp_path + path, 'w')
                                local_file.write(b.getvalue())

                    except Exception, e:
                        Log.objects.create(user=author, message=e, passed=False)
                    else:
                        Log.objects.create(user=author, message=commit_msg, passed=True)   
                    finally:
                        local_file.close()
                        curl.close()


            finally:
                ftp.quit()

    return HttpResponse()
