# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
import time
from sh.core.forms import RegistrationForm
from sh.core.models import User

def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            u = User(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            u.save()
            u.generate_password()
            
            messages.success(request, 'The user was created successfully, check your email for the password')
            return redirect(reverse('django.contrib.auth.views.login'))

    return render(request, 'registration/register.html',
                  {'form': form})

@csrf_exempt
def backup_auto (request):
    if request.method == 'POST':
        u = get_object_or_404(User, username=request.POST.get('username'))
        if u.check_password(request.POST.get('password')):
            #TODO: Fill this
            name = ''
            db_username = ''
            with open('/django_projects/db_pw/', 'rb') as f:
                db_password = f.readline()
            db_password = db_password.replace("\n","").strip()
            import os
            path = os.path.join(settings.ROOTPATH, "backups/" + name + '-' + time.strftime('%y-%m-%d-%H-%M') + '.sql')
            command = 'mysqldump -h 127.0.0.1 -u ' + db_username + ' --password=' + db_password + ' ' + name + ' > ' + path
            result = os.system(command)
            if result > 0: return HttpResponse('Could not make a backup' + str(result) + '\n' + path)
            else:
                abspath = open(path,'r')
                response = HttpResponse(content=abspath.read())
                response['Content-Type']= 'application/octet-stream'
                response['Content-Disposition'] = 'attachment; filename=%s'\
                % os.path.basename(path)
            return response
    raise 404
