# coding=utf-8
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader, Context
from django.template.loader_tags import ExtendsNode
from django.utils.crypto import get_random_string
from json import dumps
from django.views.decorators.csrf import csrf_exempt
from django.forms import ModelForm


def redirect(to, args=None, kwargs=None):
    try:
        url = reverse(to, args=args, kwargs=kwargs)
    except Exception:
        if args is None and kwargs is None:
            url = to
        else:
            raise
    return HttpResponseRedirect(url)


def change_block_names(template, change_dict):
    """
    This function will rename the blocks in the template from the
    dictionary. The keys in th change dict will be replaced with
    the corresponding values. This will rename the blocks in the
    extended templates only.
    """
    extend_nodes = template.nodelist.get_nodes_by_type(ExtendsNode)
    if len(extend_nodes) == 0:
        return
    extend_node = extend_nodes[0]
    blocks = extend_node.blocks
    for name, new_name in change_dict.items():
        if name in blocks:
            block_node = blocks[name]
            block_node.name = new_name
            blocks[new_name] = block_node
            del blocks[name]


def render_to_response(template, request, data=None, block_changes=None):
    """
    Renders the given template with given data and returns the HttpResponse

    @type request: django.http.HttpRequest
    @param request: The request object

    @type data: dict
    @param data: The extra variables that has to be passed to the context

    @type template: string
    @param template: The name of the template to be rendered

    @rtype: HttpResponse
    """
    context = RequestContext(request, data)
    template = loader.get_template(template)

    if isinstance(block_changes, dict):
        change_block_names(template, block_changes)

    html = template.render(context)
    return HttpResponse(html)


def render_template(request, template, data=None, url_params=None, **kwargs):
    if url_params is not None:
        if data is None:
            data = dict()

        for url_param in url_params:
            param_value = kwargs.get(url_param, '')
            if param_value != "":
                data[url_param] = param_value
    return render_to_response(template, request, data)


def download_string(contents, file_name):
    import mimetypes

    content_type = mimetypes.guess_type(file_name)[0]
    response = HttpResponse(contents, content_type=content_type)
    response['Content-Length'] = len(contents)
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    return response


def render_json(dictionary):
    string = dumps(dictionary)
    mimetype = 'application/json'
    return HttpResponse(string, mimetype=mimetype)


def render_jsonp(dictionary, callback):
    string = dumps(dictionary)
    mimetype = 'application/json'
    string = callback + '(' + string + ');'
    return HttpResponse(string, mimetype=mimetype)


def render_to_string(template, values=None, request=None):
    template = loader.get_template(template)
    if request is None:
        context = Context(values)
    else:
        context = RequestContext(request, values)
    html = template.render(context)
    return html


def is_response(response):
    return isinstance(response, HttpResponse)


def render_form(request, FormClass, RendererClass, form_template='forms.html', form_variable='form', instance=None, extra_dict=None, should_save=True):
    if issubclass(FormClass, ModelForm):
        form = FormClass(request.POST or None, request.FILES or None, instance=instance)
    else:
        form = FormClass(request.POST or None, request.FILES or None)
    if form.is_valid():
        try:
            obj = form.save(should_save)
            return obj
        except Exception:
            return form

    if extra_dict is None:
        extra_dict = {}

    extra_dict[form_variable] = RendererClass(form, request)
    return render_to_response(form_template, request, extra_dict)


@csrf_exempt
def delete_items_ajax(request, Model):
    """
    A generic view to delete items from a model using ajax.
    @param request:
    @type request: django.http.HttpRequest
    @return:
    """
    if request.is_ajax():
        values = request.POST.getlist('values[]')
        query = Model.objects.filter(pk__in=values)
        query.delete()
        return HttpResponse('true')
    return HttpResponse('false')


def bootstrap_message(
        request,
        heading,
        message,
        box_color='info',

        btn_1_text='',
        btn_1_color='',
        btn_1_url='',

        btn_2_text='',
        btn_2_color='',
        btn_2_url='',
        base_name='base.html',
):
    return render_to_response('django-helpers/twitter-bootstrap/message.html', request, {
        'message_heading': heading,
        'message': message,
        'box_color': box_color,
        'base_name': base_name,

        'btn_1_url': btn_1_url,
        'btn_1_text': btn_1_text,
        'btn_1_color': btn_1_color,

        'btn_2_url': btn_2_url,
        'btn_2_text': btn_2_text,
        'btn_2_color': btn_2_color,
    })


def bootstrap_error(
        request,
        message,
        heading='Error Occured !',
        box_color='danger',

        btn_1_text='',
        btn_1_color='',
        btn_1_url='',

        btn_2_text='',
        btn_2_color='',
        btn_2_url='',
        base_name='base.html',
):
    return bootstrap_message(
        request,
        heading,
        message,
        box_color,

        btn_1_text,
        btn_1_color,
        btn_1_url,

        btn_2_text,
        btn_2_color,
        btn_2_url,
        base_name
    )


def bootstrap_info(
        request,
        message,
        heading='Information',
        box_color='info',

        btn_1_text='',
        btn_1_color='',
        btn_1_url='',

        btn_2_text='',
        btn_2_color='',
        btn_2_url='',
        base_name='base.html',
):
    return bootstrap_message(
        request,
        heading,
        message,
        box_color,

        btn_1_text,
        btn_1_color,
        btn_1_url,

        btn_2_text,
        btn_2_color,
        btn_2_url,
        base_name
    )


def bootstrap_success_message(
        request,
        message,
        heading='Success',
        box_color='success',

        btn_1_text='',
        btn_1_color='',
        btn_1_url='',

        btn_2_text='',
        btn_2_color='',
        btn_2_url='',
        base_name='base.html',
):
    return bootstrap_message(
        request,
        heading,
        message,
        box_color,

        btn_1_text,
        btn_1_color,
        btn_1_url,

        btn_2_text,
        btn_2_color,
        btn_2_url,
        base_name
    )


def bootstrap_confirm(
        request,
        heading,
        message,
        yes_color='success',
        yes_text='Yes',
        cancel_color='danger',
        cancel_text='No',
        cancel_url='',
        box_color='info',
        base_name='base.html'):
    if request.method == 'POST':
        confirm = request.session['confirm_value']
        assert request.POST.get('confirm') == confirm, "Error"
        return request.POST.get('submit_button') == yes_text
    else:
        confirm = get_random_string(16)
        request.session['confirm_value'] = confirm
        return render_to_response('django-helpers/twitter-bootstrap/confirm.html', request, {
            'confirm_value': confirm,

            'confirm_heading': heading,
            'message': message,
            'base_name': base_name,
            'box_color': box_color,

            'yes_color': yes_color,
            'yes_text': yes_text,

            'cancel_color': cancel_color,
            'cancel_text': cancel_text,
            'cancel_url': cancel_url,
        })