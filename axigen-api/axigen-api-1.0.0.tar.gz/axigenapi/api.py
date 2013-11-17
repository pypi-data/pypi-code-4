#!/usr/bin/env python

'''
Axigen API module
'''

from axigenapi import telnet as ntel


class api(ntel.client):
    '''
    Axigen CLI API class
    '''

    '''Are we connected to the Axigen interface?'''
    _connected = False

    '''Last received buffer'''
    _last_received = None

    '''Last status string (+OK, +ERR:.......)'''
    _last_status = None

    '''Last error during work with Axigen CLI API'''
    _last_error = None

    '''Characters to strip from strings which are returned by Axigen'''
    _chars_to_strip = " \r\n\t"

    '''Default storage path'''
    _default_domain_storage = "/var/opt/axigen/domains/"

    def __init__(self, hostname='localhost', port=7000, timeout=5.0):
        '''
            :param str hostname: Hostname or IP address of Axigen server
            :param int port: Port of the Axigen CLI service
            :param float timeout: Timeout in seconds for connecting to
                Axigen CLI
        '''
        hostname = str(hostname).strip()
        port = int(port)
        timeout = float(timeout)
        super(api, self).__init__(hostname, port, timeout, 0)

    def __del__(self):
        if (self._connected):
            self._send_command('EXIT')
        super(api, self).__del__()

    def connect(self):
        '''
        Connects to Axigen CLI API interface
            :return: bool
        '''
        banner = self.receive(True)
        if (banner):
            self._last_received = banner
            banners = banner.split("\n")
            try:
                last_line = banners.pop().strip(self._chars_to_strip)
            except IndexError:
                last_line = banner.strip(self._chars_to_strip)
            if (last_line == '<login>'):
                self._connected = True
                return(True)
            self._connected = False
        return(False)

    def login(self, username='', password=''):
        '''
        Axigen CLI API login method
            :param str username: Axigen CLI admin username
            :param str password: Axigen CLI admin password
            :return: bool
        '''
        if (username == '' or password == ''):
            return(False)
        # Check if system is waiting for us to log in
        if (self._connected is False):
            self.connect()
        if (self._connected):
            prompt = self.get_prompt()
            if (prompt == '<login>'):
                self._send_command('user %s' % (username))
                prompt = self.get_prompt()
                if (prompt == '<password>'):
                    self._send_command(password)
                    outcome = self._last_status
                    if (outcome):
                        if (outcome[0:3] == '+OK'):
                            return(True)
                        else:
                            self._last_error = outcome
                    else:
                        self._last_error = \
                            "Unknown error while sending password"
                else:
                    self._last_error = \
                        "Unknown error while sending username"
        return(False)

    def commit(self):
        '''
        This command saves the changes and also writes these changes to the
        server configuration. This also includes the changes done in child
        contexts and saved with DONE. A switch back to the previous context
        is also done.
            :return: bool
        '''
        if (self._connected):
            status = self._send_command('COMMIT', shot_receive=False)
            if (status and not self._is_last_error()):
                return(True)
        return(False)

    def back(self, all_the_way=True, allow_exit=True, max_depth=5):
        '''
        This command, cancels any changes (where it applies) and switches
        back to the previous context. This is available from every context
        except Login and Root.
            :param bool all_the_way: Do we go back all the way or just one
                small step?
            :param bool allow_exit: Allow us to exit Axigen CLI while
                going back?
            :param int max_depth: Max depth of going back
            :return: bool
        '''
        prompt = self.get_prompt()
        max_depth = int(max_depth)
        if (prompt):
            status = False
            if (prompt in ['<#>', '<login>']):
                # If we are at the root or login context, exit the admin
                # interface
                if (allow_exit):
                    status = self._send_command('EXIT')
                    self._connected = False
            elif (prompt == '<password>'):
                # If we are at input password phase, we enter invalid
                # password and then exit the interface
                status = self._send_command('EXIT')
                if (allow_exit):
                    status = self._send_command('EXIT')
                    self._connected = False
            else:
                # If we are at some context, exit the context
                counter = 0
                status = False
                while (prompt not in ['<#>', '<login#>'] and
                  counter < max_depth):
                    status = self._send_command('BACK', shot_receive=True)
                    prompt = self.get_prompt()
                    counter += 1
            if (status and not self._is_last_error()):
                return(True)
        # No connection, nothing to do here
        return(False)

    def help(self):
        '''
        Example of long return
            :return bool:
        '''
        if (self._can_send()):
            return(self._send_command('help', True, False))
        return(False)

    def context_root(self):
        '''
        Switches to root context
            :return bool:
        '''
        status = True
        prompt = self.get_prompt()
        if (prompt != '<#>'):
            status = self.back(all_the_way=True, allow_exit=False)
        return(status)

    def context_server(self):
        '''
        Enters the Server context where you can modify server specific
        configuration
            :return bool:
        '''
        return(self._switch_context('SERVER', ['<server#>'], ['<#>']))

    def context_server_userdb(self):
        '''
        Enters the Users DB context where you can modify... users db.
            :return bool:
        '''
        prompt = self.get_prompt()
        if (prompt != '<server-userdb#>'):
            pre_status = self.context_server()
            if (pre_status):
                status = self._switch_context(
                    'USERDB', ['<server-userdb#>'], ['<server#>']
                )
                return(status)
            return(False)
        return(True)

    def context_aacl(self):
        '''
        To manage the right of the server administrators
            :return bool:
        '''
        return(self._switch_context('AACL', ['<aacl#>']))

    def context_queue(self):
        '''
        To manage the Axigen Queue
            :return bool:
        '''
        return(self._switch_context('QUEUE', ['<queue#>']))

    def context_domain_update(self, domain=''):
        '''
        Switches context to domain update mode
            :return bool:
        '''
        domain = self._sanitize_input(domain)
        if (domain == ''):
            return(False)
        context_status = self.context_root()
        if (context_status):
            # Maybe move this to _switch_named_context() method?
            command = "UPDATE Domain %s" % (domain)
            switch_status = self._send_command(command, shot_receive=False)
            if (switch_status and not self._is_last_error()):
                return(True)
        return(False)

    def context_domain_adminlimits(self, domain=''):
        '''
        Switches to context for managined domain admin limits
            :param str domain: Domain name to be used
            :return: bool
        '''
        precontext_status = self.context_domain_update(domain)
        if (precontext_status):
            status = self._send_command('CONFIG adminLimits')
            if (status and not self._is_last_error()):
                return(True)
        return(False)

    def context_domain_account_edit(self, domain='', account=''):
        '''
        Switches to context for managined domain accounts
            :param str domain: Domain name to be used
            :param str account: Account name to be used
            :return: bool
        '''
        account = self._sanitize_input(account)
        if (account == ''):
            return(False)
        precontext_status = self.context_domain_update(domain)
        if (precontext_status):
            command = 'UPDATE Account name "%s"' % (account)
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                return(True)
        return(False)

    def create_domain(self, domain_name='', postmaster_pass='!d3fp&4ss_'):
        '''
        Creates a domain
            :param str domain_name: Domain name to be created
            :param str postmaster_pass: Password for the postmaster user
            :return bool:
        '''
        # Attempt to sanitize the input data
        domain_name = self._sanitize_input(domain_name)
        postmaster_pass = self._sanitize_input(postmaster_pass)
        if (domain_name == ''):
            return(False)
        postmaster_pass = str(postmaster_pass).strip()
        if (postmaster_pass == ''):
            return(False)
        domain_location = "%s%s" %  \
            (self._default_domain_storage, domain_name)
        context_status = self.context_root()
        if (context_status):
            command = 'CREATE Domain name "%s" domainLocation "%s" ' \
                'postmasterPassword "%s"'
            command = command % \
                (domain_name, domain_location, postmaster_pass)
            status = self._send_command(command)
            if (status is not False):
                status = self.commit()
                if (status is not False and not self._is_last_error()):
                    return(True)
        return(False)

    def add_domain_alias(self, base_domain='', alias_domain=''):
        '''
        Adds domain alias to the base domain
            :param str base_domain: Domain to which we are adding a domain
                alias
            :param str alias_domain: Alias domain to be added
            :return: bool
        '''
        base_domain = self._sanitize_input(base_domain)
        alias_domain = self._sanitize_input(alias_domain)
        if (base_domain == '' or alias_domain == ''):
            return(False)
        context_status = self.context_domain_update(base_domain)
        if (context_status):
            command = 'ADD Alias "%s"' % (alias_domain)
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                commitstatus = self.commit()
                if (commitstatus and not self._is_last_error()):
                    return(True)
        return(False)

    def authorize_admin_for_domain(
        self, domain='', admin='', password='', create_admin=True
    ):
        '''
        Authorizes admin for managing domain on axigen
            :param str domain: Domain to be assigned for management
            :param str admin: Admin username for the domain management
            :param str password: Password for the admin user
            :param bool create_admin: Should we create admin (True) or
                edit existing admin (False)?
            :return: bool
        '''
        domain = self._sanitize_input(domain)
        admin = self._sanitize_input(admin)
        password = self._sanitize_input(password)
        if (domain == '' or admin == '' or password == ''):
            return(False)
        context_status = self.context_aacl()
        if (context_status):
            precommand = ''
            if (create_admin):
                precommand = 'ADD admin-user name "%s" password "%s"' \
                    % (admin, password)
            else:
                precommand = 'UPDATE admin-user name "%s"' % (admin)
            prestatus = self._send_command(precommand)
            if (prestatus):
                command = 'GRANT permission (manageAccounts) domain "%s"' \
                    % (domain)
                status = self._send_command(command)
                if (status):
                    poststatus = self._send_command("DONE")
                    if (poststatus):
                        commitstatus = self._send_command("DONE")
                        if (commitstatus):
                            return(True)
        return(False)

    def create_account(self, domain='', username='', password='#63f7&4ss_'):
        '''
        Creates one account for the domain
            :param str domain: Domain name to be used
            :param str username: Username for the account
            :param str password: Password for the account
            :return: bool
        '''
        domain = self._sanitize_input(domain)
        username = self._sanitize_input(username)
        password = self._sanitize_input(password)
        if (domain == '' or username == '' or password == ''):
            return(False)
        context_status = self.context_domain_update(domain)
        if (context_status):
            command = 'ADD Account name "%s" password "%s"' % \
                (username, password)
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                commitstatus = self.commit()
                if (commitstatus and not self._is_last_error()):
                    return(True)
        return(False)

    def change_account_password(self, domain='', username='', password=''):
        '''
        Changes the account password (use postmaster account to change
        "domain password").
            :param str domain: Domain name to be used
            :param str username: Account name to be used
            :param str password: Desired new password
            :return: bool
        '''
        password = self._sanitize_input(password)
        if (password == ''):
            return(False)
        context_status = \
            self.context_domain_account_edit(domain, username)
        if (context_status):
            command = 'SET password "%s"' % (password)
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                commitst1 = self.commit()
                commitst2 = self.commit()
                if (commitst1 and commitst2):
                    return(True)
        return(False)

    def change_admin_password(self, admin_name='', password=''):
        '''
        Changes admin password
            :param str admin_name: Admin username
            :param str password: New desired password
            :return: bool
        '''
        admin_name = self._sanitize_input(admin_name)
        password = self._sanitize_input(password)
        if (admin_name == '' or password == ''):
            return(False)
        context_status = self.context_aacl()
        if (context_status):
            precommand = 'UPDATE admin-user name "%s"' % (admin_name)
            prestatus = self._send_command(precommand)
            if (prestatus):
                command = 'SET password "%s"' \
                    % (password)
                status = self._send_command(command)
                if (status):
                    poststatus = self._send_command("DONE")
                    if (poststatus):
                        commitstatus = self._send_command("DONE")
                        if (commitstatus):
                            return(True)
        return(False)

    def create_accounts(self, domain='', accountlist=[]):
        '''
        Creates desired accounts for the domain.
            :param str domain: Domain name to be used
            :param accountlist: List of accounts
            :type accountlist: list containing dictionaries
            :return: list
        '''
        domain = self._sanitize_input(domain)
        accountlist = list(accountlist)
        returnlist = {}
        for acc in accountlist:
            username = ''
            password = ''
            try:
                username = acc['user']
                password = acc['password']
            except IndexError:
                username = ''
                password = ''
            if (username != '' and password != ''):
                returnlist[username] = \
                    self.create_account(domain, username, password)
        return(returnlist)

    def delete_admin_user(self, admin_username=''):
        '''
        Deletes admin user from the system
            :param str admin_username: Admin username
            :return: bool.
        '''
        context_status = self.context_aacl()
        if (context_status):
            command = 'REMOVE admin-user "%s"' % (admin_username)
            status = self._send_command(command, shot_receive=False)
            if (status and not self._is_last_error()):
                return(True)
        return(False)

    def delete_domain(self, domain_name=''):
        '''
        Deletes a domain from the server using the name parameter
            :param str domain_name: Domain name of a domain we want deleted
            :return: bool
        '''
        domain_name = self._sanitize_input(domain_name)
        if (domain_name == ''):
            return(False)
        command = 'DELETE Domain name "%s"' % (domain_name)
        context_status = self.context_root()
        if (context_status):
            status = self._send_command(command, shot_receive=False)
            if (status is not False and not self._is_last_error()):
                return(True)
        return(False)

    def delete_domain_alias(self, base_domain='', alias_domain=''):
        '''
        Adds domain alias to the base domain
            :param str base_domain: Domain which we are deleting a
                domain alias from
            :param str alias_domain: Alias domain to be added
            :return: bool
        '''
        base_domain = self._sanitize_input(base_domain)
        alias_domain = self._sanitize_input(alias_domain)
        if (base_domain == '' or alias_domain == ''):
            return(False)
        context_status = self.context_domain_update(base_domain)
        if (context_status):
            command = 'REMOVE Alias "%s"' % (alias_domain)
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                commitstatus = self.commit()
                if (commitstatus and not self._is_last_error()):
                    return(True)
        return(False)

    def delete_domain_admin(self, admin=''):
        '''
        Deletes admin user delegated for the domain
            :param str admin: Admin username for the domain management
            :return: bool
        '''
        admin = self._sanitize_input(admin)
        if (admin == ''):
            return(False)
        context_status = self.context_aacl()
        if (context_status):
            command = 'REMOVE admin-user name %s' % (admin)
            status = self._send_command(command)
            if (status):
                self.back()
                return(True)
        return(False)

    def disable_domain(self, domain_name=''):
        '''
        Deactivates a domain from the server
            :param str domain_name: Domain name of a domain we want disabled
            :return: bool
        '''
        domain_name = self._sanitize_input(domain_name)
        if (domain_name == ''):
            return(False)
        command = 'DISABLE Domain name "%s"' % (domain_name)
        context_status = self.context_root()
        if (context_status):
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                return(True)
        return(False)

    def enable_domain(self, domain_name=''):
        '''
        Deactivates a domain from the server
            :param str domain_name: Domain name of a domain we want disabled
            :return: bool
        '''
        domain_name = self._sanitize_input(domain_name)
        if (domain_name == ''):
            return(False)
        command = 'ENABLE Domain name "%s"' % (domain_name)
        context_status = self.context_root()
        if (context_status):
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                return(True)
        return(False)

    def list_all_domains(self, wildcard=''):
        '''
        Lists all the domains (active and inactive) of this server
            :param str wildcard: Wildcard for domain filtering
            :return: list
        '''
        wildcard = self._sanitize_input(wildcard)
        command = 'LIST AllDomains'
        if (wildcard != ''):
            command = "%s %s" % (command, wildcard)
        contextstatus = self.context_root()
        status = False
        if (contextstatus):
            status = self._send_command(command, shot_receive=False)
            if (status and not self._is_last_error()):
                parsed = self._parse_axigen_return()
                return(parsed)
        return(False)

    def list_admin_domains(self, admin=''):
        '''
        Lists domains delegated to the admin user
            :param str admin: Admin username for the domain management
            :return: bool
        '''
        admin = self._sanitize_input(admin)
        if (admin == ''):
            return(False)
        context_status = self.context_aacl()
        domains = []
        if (context_status):
            precommand = ''
            precommand = 'UPDATE admin-user name "%s"' % (admin)
            prestatus = self._send_command(precommand)
            if (prestatus):
                command = 'SHOW'
                status = self._send_command(command)
                if (status):
                    lines = self._last_received.split("\n")
                    for line in lines:
                        if line[:22] == 'Permissions on Domain ':
                            domains.append(line[23:-3])
                    self.back()
                    return(domains)
                self.back()
        return(False)

    def list_all_accounts(self, domain='', wildcard=''):
        '''
        Lists accounts for current domain
            :param str domain: Domain name for the accounts
            :param str wildcard: Wildcard for account filtering
            :return: list
        '''
        domain = self._sanitize_input(domain)
        wildcard = self._sanitize_input(wildcard)
        if (domain == ''):
            return(False)
        contextstatus = self.context_domain_update(domain)
        if (contextstatus):
            command = "LIST Accounts"
            if (wildcard != ''):
                command = "%s %s" % (command, wildcard)
            commandstatus = self._send_command(command)
            if (commandstatus and not self._is_last_error()):
                parsed = self._parse_axigen_return()
                return(parsed)
        return(False)

    def list_admin_users(self):
        '''
        Lists all admin users
            :return: List.
        '''
        context_status = self.context_aacl()
        if (context_status):
            command = "LIST admin-users"
            status = self._send_command(command, shot_receive=False)
            if (status and not self._is_last_error()):
                parsed = self._parse_axigen_return()
                return(parsed)
        return(False)

    def list_domain_aliases(self, base_domain=''):
        '''
        Adds domain alias to the base domain
            :param str base_domain: Domain which we are deleting a
                domain alias from
            :return: list
        '''
        base_domain = self._sanitize_input(base_domain)
        if (base_domain == ''):
            return(False)
        context_status = self.context_domain_update(base_domain)
        if (context_status):
            status = self._send_command("LIST Aliases")
            if (status and not self._is_last_error()):
                parsed = self._parse_axigen_special_return(
                    'The list of aliases for this domain:',
                    self.get_last_return(), 'alias'
                )
                return(parsed)
        return(False)

    def set_max_accounts(self, domain='', max_accounts=50):
        '''
        Set the max accounts for the domain
            :param str domain: Domain name to be used
            :param int max_accounts: Max number of e-mail accounts for the
                domain
            :return: bool
        '''
        max_accounts = int(max_accounts)
        if (max_accounts < 0):
            return(False)
        context_status = self.context_domain_adminlimits(domain)
        if (context_status):
            command = "SET maxAccounts %s" % (max_accounts)
            status = self._send_command(command)
            if (status and not self._is_last_error()):
                # Need two commits, it's a subcontext
                commitst1 = self.commit()
                commitst2 = self.commit()
                if (commitst1 and commitst2):
                    return(True)
        return(False)

    def get_domain_utilization(self, domain=''):
        '''
        Returns number of e-mail accounts created under the domain in Axigen
            :param str domain: Domain name for the check
            :return: int
        '''
        acc_list = self.list_all_accounts(domain)
        if (acc_list is not False):
            return(len(acc_list))
        return(False)

    def get_version(self):
        '''
        Retrieves version from the Axigen service
            :return: list
        '''
        version = self._send_command('GET VERSION', shot_receive=True)
        if (version is not False):
            version_line = version.split('\n')[0]
            return(self._return(version_line, version))
        return(False)

    def get_last_error(self):
        '''
        Returns last registered error from the Axigen CLI API
            :return: str
        '''
        return(self._last_error)

    def get_last_return(self):
        '''
        Returns last registered reply from the Axigen CLI API
            :return: str
        '''
        return(self._last_received)

    def get_prompt(self, data=''):
        '''
        Returns the last prompt from the axigen engine
            :param [str data]: Data from the axigen we want investigated
                (if nothing is sent, we use last received reply)
            :return: str
        '''
        data = str(data).strip(self._chars_to_strip)
        if (data == ''):
            data = str(self._last_received).strip(self._chars_to_strip)
        data_split = data.split('\n')
        line = None
        try:
            line = data_split.pop()
        except IndexError:
            line = data
        line = line.strip(self._chars_to_strip)
        if (line != ''):
            if (line[0:1] == '<' and line[-1] == '>'):
                return(line)
        return(False)

    def _switch_context(
        self, context='', expected_prompts=[], pre_prompts=['<#>']
    ):
        '''
        Logic for switching contexts
            :param str context: Desired context name
            :param list expected_prompts: Prompts which are expected on
                successful context switch
            :param list pre_prompts: Prompts which are expected prior to
                successful context switch
            :return: bool
        '''
        context = str(context).strip()
        if (expected_prompts == str(expected_prompts)):
            expected_prompts = [expected_prompts]
        if (pre_prompts == str(pre_prompts)):
            pre_prompts = [pre_prompts]
        if (context == '' or len(expected_prompts) == 0):
            return(False)
        command = ''
        if (context.lower() in ['aacl', 'queue']):
            command = "ENTER %s" % (context)
        else:
            command = "CONFIG %s" % (context)
        prompt = self.get_prompt()
        if (prompt not in pre_prompts and prompt not in expected_prompts):
            self.back(all_the_way=True, allow_exit=False)
        if (prompt not in expected_prompts):
            status = self._send_command(command)
            if (status):
                new_prompt = self.get_prompt()
                if (new_prompt in expected_prompts):
                    return(True)
                else:
                    return(False)
            else:
                return(False)
        return(True)

    def _sanitize_input(self, input=''):
        '''
        Sanitize input variables for Axigen CLI commands
            :param str input: Input data
            :return: str
        '''
        input = str(input).strip()
        # Kill off newlines
        input = input.replace('\n', '').replace('\r', '')
        # Escape quotes and stuff
        input = input.replace("\"", "\\\"")
        return(input)

    def _can_send(self):
        '''
        Can we send data in?
            :return: bool
        '''
        prompt = self.get_prompt()
        if (prompt == "<#>"):
            return(True)
        return(False)

    def _is_last_error(self):
        '''
        Is the last status an error?
            :return: bool
        '''
        if (self._last_status[0:4] == '-ERR'):
            self._last_error = str(self._last_status[5:]).strip()
            return(True)
        return(False)

    def _return(self, parsed='', original=''):
        '''
        Forms an answer object for Axigen data (for health checks)
            :param str parsed: Parsed answer from the Axigen
            :param str original: Original (untouched) answer from the Axigen
            :return: list
        '''
        return({
            'parsed': parsed,
            'original': original,
            'prompt': self.get_prompt(original)
        })

    def _validate_axigen_return(self, data=''):
        '''
        Validates data returned from Axigen service.
            :param [str data]: Data from the axigen we want investigated
                (if nothing is sent, we use last received reply)
            :return: bool
        '''
        data = str(data).strip(self._chars_to_strip)
        if (data == ''):
            data = str(self._last_received).strip(self._chars_to_strip)
        data_split = data.split('\n')
        # Pull last and second to last line
        try:
            last = data_split.pop()
        except IndexError:
            last = data
        try:
            last_second = data_split.pop()
        except IndexError:
            last_second = ''
        del(data_split)
        returnstatus = False
        if (last[0:3] == '+OK' or last[0:4] == '-ERR'):
            # Treat succesful operations
            self._last_status = last
            self._is_last_error()
            returnstatus = True
        elif (last_second[0:3] == '+OK' or last_second[0:4] == '-ERR'):
            self._last_status = last_second
            self._is_last_error()
            returnstatus = True
        else:
            # Unhandled situation
            self._last_status = None
            returnstatus = False
        return(returnstatus)

    def _parse_axigen_return(self):
        '''
        Parses Axigen returns to hashes
            :return: list
        '''
        if (str(self._last_received).strip() == ''):
            return(False)
        # Extract header info
        temp_split = self._last_received.split('\n')
        split_len = len(temp_split)
        headers = []
        pattern = '-' * 6
        headerlineno = -1
        lineno = 0
        foundpattern = False
        line = temp_split.pop()
        while ((not foundpattern) and line):
            if (line[0:6] == pattern):
                foundpattern = True
                headerlineno = lineno - 2
            try:
                line = temp_split.pop(0)
            except IndexError:
                line = None
                break
            lineno += 1
        del(temp_split)
        # Found header line, parse on
        split_return = self._last_received.split('\n')
        if headerlineno > -1:
            headerline = split_return[headerlineno]\
                .strip(self._chars_to_strip).lower()
            while (headerline.find('  ') != -1):
                headerline = headerline.replace('  ', ' ')
            headers = headerline.split(' ')
        retlist = []
        # Got headers straightened out, get the data
        for l in range(headerlineno + 2, split_len - 1):
            operline = ''
            try:
                operline = split_return[l].strip()
            except IndexError:
                operline = None
                break
            if (operline == ''):
                break
            while (operline.find('  ') != -1):
                operline = operline.replace('  ', ' ')
            opersplit = operline.split(' ')
            retitem = {}
            for hno in range(len(headers)):
                value = ''
                try:
                    value = opersplit[hno]
                except IndexError:
                    value = None
                retitem[headers[hno]] = value
            retlist.append(retitem)
        return(retlist)

    def _parse_axigen_special_return(
        self, parseline='', data='', result_identificator='data'
    ):
        '''
        Parses out Axigen returns which are special cases (not delimited
        with line containing only '---------------------------------')...
            :param str parseline: Line which marks beginning of the data
            :param str data: Return data from axigenapi
            :param str result_identificator: Identificator for results
                in returning list-dictionary [('identificator':'value')]
            :return: list
        '''
        parseline = str(parseline).strip()
        foundparseline = False
        pullingdata = False
        returnlist = []
        for line in data.split('\n'):
            if (foundparseline is False):
                if (line.find(parseline) != -1):
                    foundparseline = True
            else:
                if (line.strip(self._chars_to_strip) == ''):
                    break
                if (pullingdata is False):
                    pullingdata = True
                item = {}
                item[result_identificator] = \
                    line.strip(self._chars_to_strip)
                returnlist.append(item)
        if (len(returnlist) <= 0):
            return(False)
        return(returnlist)

    def _send_command(
        self, command='', auto_validate=True, shot_receive=False
    ):
        '''
        Send command to Axigen CLI API.
        Appends \r\n to the axigen command and then submits it to the
        Axigen service. Then it retrieves answer from the Axigen and
        return it back to the caller.
        Overrides parent's _send_command() method.
            :param str command: Command to send
            :param bool auto_validate: Should we automatically try to
                validate Axigen's return?
            :param bool shot_receive: Should we do one-hit receive,
                not waiting for all data to come to us?
            :return: str
        '''
        if (self._connected is False):
            self.connect()
        returnvalue = super(api, self)._send_command(
            command, '\r\n', shot_receive
        )
        self._last_received = returnvalue
        if (auto_validate):
            validate_status = self._validate_axigen_return(returnvalue)
            if (validate_status is not False):
                return(returnvalue)
        else:
            return(returnvalue)
