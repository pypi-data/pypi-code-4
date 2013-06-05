# (C) HawkOwl, 2013

import json
import urllib

from twisted.internet import reactor, defer
from twisted.internet.defer import Deferred, succeed, failure, maybeDeferred
from twisted.internet.protocol import Protocol
from twisted.web.client import getPage


class DNSManager:

    def __init__(self, apikey, apipath = "https://api.linode.com/?", debug = False):

        self.apikey = apikey
        self.apipath = apipath
        self.debug = debug

    def sendcommand(self, method, command):

        def _normalise(result):

            res = json.loads(result)

            if res['ERRORARRAY']:
                return failure.Failure(exc_value=res['ERRORARRAY'][0]['ERRORMESSAGE'])

            return res['DATA']

        command['api_action'] = method
        command['api_key'] = self.apikey
        params = urllib.urlencode(command)

        if self.debug: print params

        return getPage(self.apipath + params).addCallback(_normalise)

    def echo(self):

        command = {'test': 123}

        return self.sendcommand('test.echo', command)

    def domain_create(self, Domain, Type, Description = "", SOA_Email = "", Refresh_sec = -1, Retry_sec = -1, Expire_sec = -1, TTL_sec = -1, status = -1, master_ips = "", axfr_ips = ""):

        command = {'Domain': Domain}

        if Type:
            if Type == "master":
                command['Type'] = 'master'
            elif Type == "slave":
                command['Type'] = 'slave'
            else:
                return failure.Failure(exc_value="Specify a valid Type")

        if axfr_ips: command['axfr_ips'] = axfr_ips
        if Description: command['Description'] = Description
        if Expire_sec > -1: command['Expire_sec'] = Expire_sec
        if master_ips: command['master_ips'] = master_ips
        if Refresh_sec > -1: command['Refresh_sec'] = Refresh_sec
        if Retry_sec > -1: command['Retry_sec'] = Retry_sec
        if SOA_Email: command['SOA_Email'] = SOA_Email
        if status > -1: command['status'] = status
        if TTL_sec > -1: command['TTL_sec'] = TTL_sec

        return self.sendcommand('domain.create', command)

    def domain_delete(self, DomainID):

        command = {'DomainID': DomainID}

        return self.sendcommand('domain.delete', command)

    def domain_list(self, DomainID = 0):

        command = {}

        if DomainID:
            command['DomainID'] = DomainID

        return self.sendcommand('domain.list', command)

    def domain_update(self, DomainID, Domain = "", Type = "", Description = "", SOA_Email = "", Refresh_sec = -1, Retry_sec = -1, Expire_sec = -1, TTL_sec = -1, status = -1, master_ips = "", axfr_ips = ""):

        command = {'DomainID': DomainID}

        if Type:
            if Type == "master":
                command['Type'] = 'master'
            elif Type == "slave":
                command['Type'] = 'slave'
            else:
                return failure.Failure(exc_value="Specify a valid Type")

        if axfr_ips: command['axfr_ips'] = axfr_ips
        if Description: command['Description'] = Description
        if Domain: command['Domain'] = Domain
        if Expire_sec > -1: command['Expire_sec'] = Expire_sec
        if master_ips: command['master_ips'] = master_ips
        if Refresh_sec > -1: command['Refresh_sec'] = Refresh_sec
        if Retry_sec > -1: command['Retry_sec'] = Retry_sec
        if SOA_Email: command['SOA_Email'] = SOA_Email
        if status > -1: command['status'] = status
        if TTL_sec > -1: command['TTL_sec'] = TTL_sec

        return self.sendcommand('domain.update', command)

    def domain_resource_create(self, DomainID, Type, Name = "", Target = "", Priority = -1, Weight = -1, Port = -1, Protocol = "", TTL_sec = -1):

        command = {'DomainID': DomainID, 'Type': Type}

        if Name: command['Name'] = Name
        if Port > -1: command['Port'] = Port
        if Priority > -1: command['Priority'] = Priority
        if Protocol: command['Protocol'] = Protocol
        if Target: command['Target'] = Target
        if TTL_sec > -1: command['TTL_sec'] = TTL_sec
        if Weight > -1: command['Weight'] = Weight

        return self.sendcommand('domain.resource.create', command)

    def domain_resource_delete(self, DomainID, ResourceID):

        command = {'DomainID': DomainID, 'ResourceID': ResourceID}

        return self.sendcommand('domain.resource.delete', command)

    def domain_resource_list(self, DomainID, ResourceID = 0):

        command = {'DomainID': DomainID}

        if ResourceID:
            command['ResourceID'] = ResourceID

        return self.sendcommand('domain.resource.list', command)

    def domain_resource_update(self, DomainID, ResourceID, Type = "", Name = "", Target = "", Priority = -1, Weight = -1, Port = -1, Protocol = "", TTL_sec = -1):

        command = {'DomainID': DomainID, 'ResourceID': ResourceID}

        if Name: command['Name'] = Name
        if Port > -1: command['Port'] = Port
        if Priority > -1: command['Priority'] = Priority
        if Protocol: command['Protocol'] = Protocol
        if Target: command['Target'] = Target
        if TTL_sec > -1: command['TTL_sec'] = TTL_sec
        if Type: command['Type'] = Type
        if Weight > -1: command['Weight'] = Weight

        return self.sendcommand('domain.resource.update', command)