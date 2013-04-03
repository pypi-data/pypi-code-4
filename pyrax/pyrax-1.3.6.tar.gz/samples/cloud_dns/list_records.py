#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2012 Rackspace

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys

import pyrax
import pyrax.exceptions as exc


creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
dns = pyrax.cloud_dns

PAGE_SIZE = 10
count = 0
domain_name = "abc.example.edu"

def print_records(records):
    for record in records:
        print "Record:", record.type
        print "  ID:", record.id
        print "  data:", record.data
        print "  TTL:", record.ttl
        print "  comment:", record.comment
        print

try:
    dom = dns.find(name=domain_name)
except exc.NotFound:
    answer = raw_input("The domain '%s' was not found. Do you want to create "
            "it? [y/n]" % domain_name)
    if not answer.lower().startswith("y"):
        sys.exit()
    try:
        dom = dns.create(name=domain_name, emailAddress="sample@example.edu",
                ttl=900, comment="sample domain")
    except exc.DomainCreationFailed as e:
        print "Domain creation failed:", e
    print "Domain created:", dom
    print

records = dom.list_records(limit=PAGE_SIZE)
count += len(records)
print_records(records)

# Loop until all records are printed
while True:
    try:
        records = dns.list_records_next_page()
        count += len(records)
    except exc.NoMoreResults:
        break
    print_records(records)

print "There were a total of %s record(s)." % count
print
