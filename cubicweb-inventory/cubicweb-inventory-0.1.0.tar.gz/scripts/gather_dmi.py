# -*- coding: utf-8 -*-
"""
Batch to create a Device (and dependencies) by reading DMI values

This script should be launched as:

cubicweb-ctl shell sysinfo gather_dmi.py user@hostname user@otherhost

.. Note:: python-dmidecode must be installed on the gathered host

"""

import sys

try:
    from subprocess import check_output
except ImportError:
    # only from python 2.7
    from subprocess import Popen, PIPE, CalledProcessError
    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output


def gather_host(host):
    dmi = eval(check_output( ["ssh", host,  "python -c 'import dmidecode; print dmidecode.system()'"]))

    for dmiv in dmi.values():
        if dmiv['dmi_type'] == 1:
            # should be the one with interesting stuff
            dmiv = dmiv['data']

            device = host.split('@')[-1]
            sn = dmiv['Serial Number']
            uuid = dmiv['UUID']
            if uuid in ('', 'not specified'):
                uuid = None
            if sn in ('', 'not specified'):
                print "oops, no serial number; skipping"
                return
            if rql('Any D WHERE D is Device, D serial %(serial)s', {'serial': sn}):
                print "serial number ", sn, "already exists; skipping"
                return

            manufacturer = dmiv['Manufacturer']
            if manufacturer.lower() not in ('', 'not specified'):

                rset = rql('Any N WHERE C is Company, C name N, C name ILIKE %(cname)s',
                           {'cname': u'%s%%'%unicode(manufacturer.split()[0])})
                # we use manuf.split()[0] cause there often is a
                # "Inc." or similar in the DMI data, eg. "Dell Inc."
                # Not bullet proof, but should behave nicely most of the time
                if rset:
                    print manufacturer, "is already known as",
                    manufacturer = rset[0][0]
                    print manufacturer
                else:
                    # we must add it
                    # XXX ask use if she wants to do so...
                    print "inserting new manufacturer", manufacturer
                    rql('INSERT Company C: C name %(cname)s', {'cname': unicode(manufacturer)})
            else:
                manufacturer = None

            model = dmiv['Product Name']
            sku = dmiv['SKU Number']
            if sku is None or sku.lower() in ('', 'not specified'):
                sku = model
            if model.lower() not in ('', 'not specified'):
                model = unicode(model)
                rset = rql('Any N WHERE M is DeviceModel, M name N, M name ILIKE %(mname)s',
                           {'mname': unicode(model)})
                if rset:
                    print model, "is already known"
                else:
                    print "inserting model", model
                    req = 'INSERT DeviceModel M: M name %(model)s, M klass %(klass)s, M model_ref %(ref)s'
                    d = {'model': unicode(model),
                         'klass': u'server', # can it be something else here ?
                         'ref': unicode(sku),}

                    if manufacturer:
                        req += ', M made_by C WHERE C name %(manufacturer)s'
                        d['manufacturer'] = manufacturer
                    rql(req, d)
            else:
                model = None
            print "inserting device", device, sn
            req = 'INSERT Device D: D name %(name)s, D serial %(serial)s'
            where = []
            if model:
                req += ', D model DM'
                where.append('DM name %(model)s')
            if where:
                req += ' WHERE ' + ', '.join(where)
            rql(req, {'name': unicode(device), 'serial': unicode(sn), 'model': model})



for host in __args__:
    gather_host(host)

commit()
