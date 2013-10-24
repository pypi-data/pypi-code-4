# -*- coding: utf-8 -*-
import datetime
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from .models import make_model_from_api
from .settings import get_viddler


@permission_required('viddler.add_viddlervideo')
def callback(request):
    """
    Handle the Viddler Callback after uploading a video
    """
    video_id = request.GET.get('videoid', '')
    if not video_id:
        raise Exception("No video id returned from Viddler")
    # viddler = get_viddler()
    # video_details = viddler.videos.getDetails(video_id)
    # video = make_model_from_api(video_details)
    return HttpResponseRedirect(reverse('viddler_download', kwargs={'videoid': video_id}))


@permission_required('viddler.add_viddlervideo')
def sync(request):
    """
    Syncronize all viddler videos from viddler

    ?since=YYYY-MM-DD
    """
    viddler = get_viddler()
    kwargs = {}
    if 'since' in request.GET:
        try:
            kwargs['min_upload_date'] = datetime.datetime.strptime('%Y-%m-%d')
        except ValueError:
            pass
    results = viddler.videos.search_yourvideos(**kwargs)
    for item in results:
        make_model_from_api(item)
    return HttpResponseRedirect(reverse('admin:viddler_viddlervideo_changelist'))


@permission_required('viddler.add_viddlervideo')
def download(request, videoid):
    """
    Download a specific viddler video into the admin (if it isn't already)
    """
    viddler = get_viddler()
    video_details = viddler.videos.getDetails(videoid)
    video = make_model_from_api(video_details)
    return HttpResponseRedirect(reverse('admin:viddler_viddlervideo_change', args=(video.id,)))


@permission_required('viddler.add_viddlervideo')
def progress(request):
    """
    Returns the progress of a video upload
    """
    if 'token' in request.GET:
        viddler = get_viddler()
        try:
            results = viddler.videos.uploadProgress(request.GET['token'])
        except viddler.ViddlerAPIException as e:
            results = {"status": 4, "percent": 0, "error": e.message}
    else:
        results = {"status": 4, "percent": 0, "error": "Upload token not found."}
    return HttpResponse(json.dumps(results), mimetype="application/json")
