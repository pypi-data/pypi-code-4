# Create your views here.
from datetime import datetime
import json

from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from pwmanager.nodes.models import Node, NodeGroup, ProvisionPackage
from django.core.files import File
from pwmanager.settings import PROVISION_PACKAGE_UPLOAD_DIRECTORY


def node_viewer(request, name):
    print(name)
    try:
        group = NodeGroup.objects.get(short_name=name)
    except Node.DoesNotExist:
        raise Http404
    return render_to_response('group.html', {
        'group_nodes': json.dumps([x.format_full_name() for x in group.nodes.all()]),
    })

@csrf_exempt
def package_upload(request, group):

    try:
        group = NodeGroup.objects.get(short_name=group)
    except NodeGroup.DoesNotExist:
        raise Http404

    filename = 'package-%s' % datetime.now()
    filepath = '%s/%s' % (PROVISION_PACKAGE_UPLOAD_DIRECTORY, filename)

    with open(filepath, 'w+') as f:
        f.write(request.body)
        package = ProvisionPackage()
        package.group = group
        package.package = File(f, name=filename)
        package.save()

    return HttpResponse('ok')

def home(request):
    return render_to_response('home.html', {})