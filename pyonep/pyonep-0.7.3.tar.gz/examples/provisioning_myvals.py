#==========================================================================
# provisioning.py
# Demonstrates use of the provision API
#==========================================================================
##
## Tested with python 2.7.2
##
## Copyright (c) 2010, Exosite LLC
## All rights reserved.
##
import random

from pyonep.provision import Provision
from pyonep.onep import OnepV1

if __name__ == '__main__':
    # Vendor Token is available on the domain admin home page
    vendortoken = '55f5e9bbb7f3e7898aae087b2dbb203eb39d936b'
    # CIK of client to clone for model
    clonecik = '2243029aec7f5c05830dd5ba31b6052c3935d5d0'  # Exosite Device
    # CIK of parent of clonecik client. In the case of Portals,
    # this is the CIK of the portal. It can be found in your portal under
    # Account > Portals
    # Look for: Key: 123abc...
    portalcik = '7eeec3d7d8765fd0b5c2d951dc59f6f6bb16913f'
    vendor = 'weaver'

    # Name of model to create during test

    r = random.randint(1, 10000000)
    model = 'MyTestModel' + str(r)
    sn1 = '001' + str(r)
    sn2 = '002' + str(r)
    sn3 = '003' + str(r)

    op = OnepV1()
    isok, portalrid = op.lookup(portalcik, 'alias', '')
    if not isok:
        print("Failed to look up portal RID")
    else:
        print("portalrid: '{}'".format(portalrid))
    isok, clonerid = op.lookup(clonecik, 'alias', '')
    if not isok:
        print("Failed to look up clone RID")
    else:
        print("clonerid: '{}'".format(clonerid))
    provision = Provision('http://m2.exosite.com', verbose=False)
    print("model_create()")
    provision.model_create(vendortoken, model, clonerid, aliases=False)

    print provision.model_list(vendortoken)
    print provision.model_info(vendortoken, model)
    print("serialnumber_add()")
    provision.serialnumber_add(vendortoken, model, sn1)
    print("serialnumber_add_batch()")
    provision.serialnumber_add_batch(vendortoken, model, [sn2, sn3])
    print provision.serialnumber_list(vendortoken, model, limit=10)
    print("serialnumber_remove_batch()")
    provision.serialnumber_remove_batch(vendortoken, model, [sn2, sn3])
    print provision.serialnumber_list(vendortoken, model)
    print("serialnumber_enable()")
    provision.serialnumber_enable(vendortoken, model, sn1, portalrid) ## return clientid
    print "AFTER ENABLE:",provision.serialnumber_info(vendortoken, model, sn1)
    print("serialnumber_disable()")
    provision.serialnumber_disable(vendortoken, model, sn1)
    print "AFTER DISABLE:",provision.serialnumber_info(vendortoken, model, sn1)
    print("serialnumber_reenable()")
    provision.serialnumber_reenable(vendortoken, model, sn1)
    print "AFTER REENABLE:",provision.serialnumber_info(vendortoken, model, sn1)
    print("serialnumber_activate()")
    sn_cik = provision.serialnumber_activate(model, sn1, vendor) ##return client key
    print "AFTER ACTIVATE:",provision.serialnumber_info(vendortoken, model, sn1)
    content_id = "atxt"
    content_data = "This is content data"
    print("content_create()")
    provision.content_create(vendortoken, model, content_id, "This is text")
    print provision.content_list(vendortoken, model)
    print("content_upload()")
    provision.content_upload(vendortoken, model, content_id, content_data, "text/plain")
    print provision.content_info(vendortoken, model, content_id)
    print("content_download()")
    provision.content_download(sn_cik, vendor, model, content_id)
    print("content_remove()")
    provision.content_remove(vendortoken, model, content_id)
    print("model_remove()")
    provision.model_remove(vendortoken, model)
