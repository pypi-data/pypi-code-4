#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django_moip.html.nit.forms import MoipNITForm
from django_moip.html.nit.models import MoipNIT
 
 
@require_POST
@csrf_exempt
def nit(request, item_check_callable=None):
    """
    MoIP NIT endpoint (notify_url).
    Used by MoIP to confirm transactions.
    https://www.moip.com.br/AdmMainMenuMyData.do?method=transactionnotification
    
    (MoIP have no official NIT simulator)
    """
    #TODO: Clean up code so that we don't need to set None here and have a lot
    #      of if checks just to determine if flag is set.
    flag = None
    nit_obj = None
    
    # Clean up the data as MoIP sends some weird values such as "N/A"
    data = request.POST.copy()
    data_fields = ('id_transacao', 'valor', 'status_pagamento', 'cod_moip'
                   'forma_pagamento', 'tipo_pagamento', 'email_consumidor')

    form = MoipNITForm(data)
    if form.is_valid():
        try:
            #When commit = False, object is returned without saving to DB.
            nit_obj = form.save(commit = False)
        except Exception, e:
            flag = "Exception while processing. (%s)" % e
    else:
        flag = "Invalid form. (%s)" % form.errors
 
    if nit_obj is None:
        nit_obj = MoipNIT()
    
    #Set query params and sender's IP address
    nit_obj.initialize(request)

    if flag is not None:
        #We save errors in the flag field
        nit_obj.set_flag(flag)
    else:
        # Secrets should only be used over SSL.
        # btw, MoIP does not have this concept of "secret" yet!
        # (but the code will still be here)
        if request.is_secure() and 'secret' in request.GET:
            nit_obj.verify_secret(form, request.GET['secret'])
        else:
            nit_obj.verify(item_check_callable)

    nit_obj.save()
    return HttpResponse("OKAY")
