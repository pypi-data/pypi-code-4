from celery.execute import send_task
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from forms import SendSMSForm

@staff_member_required
def send_sms_view(request):
    form = SendSMSForm(request.POST or None)
    if form.is_valid():
        phone = form.data['phone']
        text = form.data['text']
        send_task('mobilvest.tasks.send_raw_sms',args=[phone,text])
    c={'form':form}
    return render_to_response("admin/send_sms.html",RequestContext(request,c))

