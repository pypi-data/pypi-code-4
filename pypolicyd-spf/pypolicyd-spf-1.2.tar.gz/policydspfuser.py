# -*- coding: utf-8 -*-
#
#  pypolicyd-spf
#  Copyright © 2010-2012 Scott Kitterman <scott@kitterman.com>
'''
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import syslog
import re
import string
import os

###############################################################
commentRx = re.compile(r'^(.*)#.*$')
def _readUserConfigFile(path, recipient, configData):
    '''Reads a configuration file from the specified path, merging it
    with the configuration data specified in configData for the identified
    recipient.  Returns updated configData for the user.'''

    debugLevel = configData.get('debugLevel', 0)
    if debugLevel >= 4: syslog.syslog('readUserConfigFile: Loading "%s"' % path)
    if configData == None: configData = {}
    nameConversion = {
            'debugLevel' : int,
            'HELO_reject' : str,
            'Mail_From_reject' : str,
            'PermError_reject' : str,
            'TempError_Defer' : str,
            'Mail_From_pass_restriction' : str,
            'HELO_pass_restriction' : str,
            'Prospective' : str,
            'Whitelist' : str,
            'skip_addresses': str,
            'Domain_Whitelist' : str,
            'Domain_Whitelist_PTR': str,
            'No_Mail': str,
            'Reject_Not_Pass_Domains' : str,
            'defaultSeedOnly' : int,
            'Header_Type' : str,
            'Authserv-Id' : str
            }

    #  check to see if it's a file
    try:
        os.stat(path)[0]
    except OSError as e:
        syslog.syslog(syslog.LOG_ERR,'ERROR stating "%s": %s' % ( path, e.strerror ))
        return(configData, False)

    #  load file
    fp = open(path, 'r')
    while 1:
        line = fp.readline()
        if not line: break

        #  parse line
        line = (line.split('#', 1)[0]).strip()
        if not line: continue
        data = [q.strip() for q in line.split(',', 1)]
        user, value = data
        if user != recipient:
            peruser = False
            continue
        values = {}
        valuelist = value.split('|')
        for valuepair in valuelist:
            key, item = valuepair.split('=')
            values[key] = item
        for config in values.items():
            #  check validity of name
            conversion = nameConversion.get(config[0])
            name, value = config
            if conversion == None:
                syslog.syslog(syslog.LOG_ERR,'ERROR: Unknown name "%s" in file "%s"' % ( name, path ))
                continue
            if debugLevel >= 5: syslog.syslog('readUserConfigFile: Found entry "%s=%s"'
                % ( name, value ))
            configData[name] = conversion(value)
        peruser = True
    fp.close()

    return configData, peruser


def _datacheck(configData, recipient):
    debugLevel = configData.get('debugLevel', 1)
    if debugLevel >= 3: syslog.syslog('Starting to process per-user settings')
    userdata = configData.get('Per_User')
    if debugLevel >= 3: syslog.syslog('User data: '+ str(userdata))
    usertype, userlocation = userdata.split(',')
    if usertype == "text":
         if debugLevel >= 4: syslog.syslog('Reading per user data (type text) from:  "%s"' % userlocation)
         configData, peruser = _readUserConfigFile(userlocation, recipient, configData)
         if debugLevel >= 4: syslog.syslog('Per-user settings for "%s": "%s"' % (recipient, str(configData)))

    return configData, peruser
