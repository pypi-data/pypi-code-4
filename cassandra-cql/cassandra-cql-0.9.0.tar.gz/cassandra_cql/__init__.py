#! /usr/bin/env python

# Copyright 2013 Andrew Mussey. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# This file is used to inject a full *.cql file into a Cassandra database.
# To run this script, all three command line parameters are required:
#
#     python cassandra-cql.py hostname port script_file
#
# An example script file would be:
#
#     USE keyspace;
#
#     CREATE COLUMNFAMILY projects (
#       KEY uuid PRIMARY KEY,
#       project_id int,
#       name text
#     );

import cql
import sys
import thrift
from cassandra_cql.bcolors import bcolors

def cql_execute(host, port, filename, force, silent=False):
    try:
        connection = cql.connect(host=host, port=port, cql_version='3.0.0')
    except thrift.transport.TTransport.TTransportException, e:
        if not silent:
            print 'Execution failed: {e}'.format(e=e)
        return False
    cursor = connection.cursor()

    cql_file = open(filename)

    cql_command_list = ''.join(cql_file.readlines()).split(";")

    for cql_command in cql_command_list:
        if cql_command.replace('\n', ''):
            if not silent:
                print '\n{command}'.format(command=cql_command.strip('\n'))

            try:
                cursor.execute('{command};'.format(command=cql_command.replace('\n', ' ')))
                if not silent:
                    print '{color_start}Success!{color_end}'.format(color_start=bcolors.OKGREEN, color_end=bcolors.ENDC)
            except cql.ProgrammingError as e:
                if not silent:
                    print '{color_start}{error}{color_end}'.format(error=e, color_start=bcolors.FAIL, color_end=bcolors.ENDC)
                if not force:
                    if not silent:
                        print '\n{color_start}Execution of script {filename} failed!\nSee the error message above for details.{color_end}'.format(color_start=bcolors.FAIL,
                                                                                                        color_end=bcolors.ENDC,
                                                                                                        filename=filename)
                    return False
    if not silent:
        print '\n{color_start}Execution of script {filename} complete!{color_end}'.format(color_start=bcolors.OKBLUE,
                                                                                          color_end=bcolors.ENDC,
                                                                                          filename=filename)

