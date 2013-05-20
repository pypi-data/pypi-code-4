# coding: utf-8

from django.utils import simplejson as json
from django.http import HttpResponse

from skypehub.utils import get_skype, SkypeError
from skypehub.forms import PostMessageForm, PostUserMessageForm


def make_json_response(content, status=200):
    return HttpResponse(
        json.dumps(content, indent=2),
        content_type='application/javascript', status=status)


def list_chats(request):
    skype = get_skype()
    chats = []
    for chat in skype.Chats:
        chats.append({
            'name': chat.Name,
            'topic': chat.Topic,
        })
    return make_json_response({'chats': chats})


def post_message(request):
    form = PostMessageForm(request.POST or None)
    try:
        skype = get_skype()
        if form.is_valid():
            chat = skype.Chat(form.cleaned_data['chat'])
            if hasattr(chat, 'AsyncSendMessage'):
                chat.AsyncSendMessage(form.cleaned_data['message'])
            else:
                chat.SendMessage(form.cleaned_data['message'])
            return make_json_response({'result': 'ok'})
        else:
            form = PostUserMessageForm(request.POST or None)
            if form.is_valid():
                if hasattr(skype, 'AsyncSendMessage'):
                    skype.AsyncSendMessage(
                        form.cleaned_data['username'],
                        form.cleaned_data['message'])
                else:
                    skype.SendMessage(
                        form.cleaned_data['username'],
                        form.cleaned_data['message'])
                return make_json_response({'result': 'ok'})
    except SkypeError, e:
        # Invalid chat name (errno=105)
        # or Sending a message to failes (errno=511)
        if e.args[0] in [105, 511]:
            return make_json_response({'result': e.args[1]}, status=403)
        else:
            raise e
    return make_json_response({'result': 'validation error.'})
