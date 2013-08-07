#!/usr/bin/env python

 ##
#
# This script is based on sp-mantis2github. More information at:
#     https://github.com/servalproject/serval-tools/blob/master/doc/sp-mantis2github.md
#
###

# mantis2xml (MantisBT issues to XML) migration tool
# Copyright 2013 Richard Gomes <rgomes.info@gmail.com>
# ----------------------------------------------------------------------------------
# Serval Project Mantis-to-Git issue migration tool.
# Copyright 2012 Serval Project Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


 ##
# The following doc comment actually defines the command-line syntax, and
# drives its parsing, via the docopt module.
###
'''Exports MantisBT issues to XML.
Usage:
    mantis2xml [options] mantis version
    mantis2xml [options] mantis wsdl
    mantis2xml [options] mantis list projects
    mantis2xml [options] mantis list project users [<project-id>]
    mantis2xml [options] mantis list enum status
    mantis2xml [options] mantis list enum resolutions
    mantis2xml [options] mantis list issue users
    mantis2xml [options] mantis list issues [<project-id>] [-C|--closed] [-O|--open]
    mantis2xml [options] mantis dump project <project-id>
    mantis2xml [options] mantis dump issue <issue-id>
    mantis2xml [options] mantis add note <issue-id> <text>
    mantis2xml -h | --help
    mantis2xml --version
Options:
    -h --help        Show this message
    --version        Show version and exit
    -D --debug       Enable debug logging
    --config=PATH    Read config file [default: $HOME/.mantis2xml]
    --url=URL        Connect to Mantis SOAP service at this URL
    --user=USER      Connect to Mantis with this user name (overrides config file)
    --password=PASS  Connect to Mantis with this password (overrides config file)
    -C --closed      When listing issues or users of issues, only include closed issues
    -O --open        When listing issues, only include open issues

The config file is in INI format.  It contains user names and passwords in the clear so it is
ignored unless owned by the caller and permissions are at most 0600.
'''

myname = 'mantis2xml'
myversion = '1.3' #TODO
myurl = 'https://launchpad.net/' + myname

import sys
import traceback
import os
import os.path
import logging
import ConfigParser
import datetime
import urllib2
import re


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds').setLevel(logging.CRITICAL)
    import docopt
    cx = Context()
    cx.opts = docopt.docopt(__doc__, version=myversion)
    #print cx.opts
    cx.config_path = os.path.expanduser(os.path.expandvars(cx.opts['--config']))
    cx.read_config_file()
    if cx.opts['--debug']:
        cx.debug_enabled = True
    cx.mantis.url = cx.opts['--url'] or cx.mantis.url
    cx.mantis.user = cx.opts['--user'] or cx.mantis.user
    cx.mantis.password = cx.opts['--password'] or cx.mantis.password
    cx.mantis.include_open = cx.opts['--open']
    cx.mantis.include_closed = cx.opts['--closed']

    if cx.debug_enabled:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('suds').setLevel(logging.INFO)

    try:
        if cx.opts['mantis']:
            if cx.opts['wsdl']:
                print cx.mantis.client()
            elif cx.opts['version']:
                print cx.mantis.service('mc_version')
            elif cx.opts['list'] and cx.opts['projects']:
                projects = cx.mantis.service_cred('mc_projects_get_user_accessible')
                projects.sort(key=lambda p: p.id)
                for project in projects:
                    print '%-5s %-15s %-15s %-40s' % (project.id, project.status.name, project.view_state.name, project.name)
            elif cx.opts['dump'] and cx.opts['project']:
                try:
                    project_id = int(cx.opts['<project-id>'])
                except ValueError:
                    fatal('invalid <project-id>')
                projects = cx.mantis.service_cred('mc_projects_get_user_accessible')
                for project in projects:
                    if project.id == project_id:
                        print project
            elif cx.opts['dump'] and cx.opts['issue']:
                try:
                    mantis_issue_id = int(cx.opts['<issue-id>'])
                except ValueError:
                    fatal('invalid <issue-id>')

                xml = cx.mantis.get_issue_asXML(mantis_issue_id)
                import lxml.etree as etree
                parser = etree.XMLParser(ns_clean=True, recover=True)
                root = etree.fromstring(xml.encode('utf-8'), parser=parser)
                dropns(root)
                attachments(root)
                print etree.tostring(root, pretty_print = True)
            elif cx.opts['list'] and cx.opts['project'] and cx.opts['users']:
                project_ids = []
                if cx.opts['<project-id>']:
                    try:
                        project_ids.append(int(cx.opts['<project-id>']))
                    except ValueError:
                        fatal('invalid <project-id>')
                all_users = cx.mantis.get_users(project_ids)
                for user in all_users.itervalues():
                    values = (getattr(user, 'name', ''), getattr(user, 'real_name', ''), getattr(user, 'email', ''))
                    if values != ('', '', ''):
                        print '%-20s %-30s %s' % values
            elif cx.opts['list'] and cx.opts['issue'] and cx.opts['users']:
                all_issues = cx.mantis.get_issues().values()
                users = {}
                for issue in all_issues:
                    try:
                        users[issue.reporter.id] = issue.reporter
                    except AttributeError:
                        pass
                    try:
                        users[issue.handler.id] = issue.handler
                    except AttributeError:
                        pass
                users = users.values()
                users.sort(key=lambda u: (getattr(u, 'name', ''), getattr(u, 'real_name', '')))
                for user in users:
                    values = (getattr(user, 'name', ''), getattr(user, 'real_name', ''), getattr(user, 'email', ''))
                    if values != ('', '', ''):
                        print '%-20s %-30s %s' % values
            elif cx.opts['list'] and cx.opts['enum'] and cx.opts['status']:
                for elt in cx.mantis.get_enum_status():
                    print elt
            elif cx.opts['list'] and cx.opts['enum'] and cx.opts['resolutions']:
                for elt in cx.mantis.get_enum_resolutions():
                    print elt
            elif cx.opts['list'] and cx.opts['issues']:
                project_ids = []
                if cx.opts['<project-id>']:
                    try:
                        project_ids.append(int(cx.opts['<project-id>']))
                    except ValueError:
                        fatal('invalid <project-id>')
                all_issues = cx.mantis.get_issues(project_ids).values()
                all_issues.sort(key=lambda p: p.id)
                for issue in all_issues:
                    flags = [' '] * 2
                    if getattr(issue, 'attachments', None):
                        flags[0] = 'A'
                    if getattr(issue, 'relationships', None):
                        flags[1] = 'R'
                    print '%-5s %-10s %-10s %s %s' % (issue.id, issue.status.name, issue.resolution.name, ''.join(flags), issue.summary)
            elif cx.opts['add'] and cx.opts['note']:
                try:
                    mantis_issue_id = int(cx.opts['<issue-id>'])
                except ValueError:
                    fatal('invalid <issue-id>')
                text = cx.opts['<text>']
                cx.mantis.debug('add_note(%r, %r)', mantis_issue_id, text)
                if not cx.dry_run:
                    cx.mantis.add_note(mantis_issue_id, text)
    except IOError, e:
        if cx.debug:
            traceback.print_exc()
        fatal('%s: %s' % (cx.mantis.url or '<Unknown URL>', e))
    except Exception, e:
        if cx.debug:
            traceback.print_exc()
        fatal(u'Error: %s' % (e,))


def dropns(root):
    for elem in root.iter():
        parts = elem.tag.split(':')
        if len(parts) > 1:
            elem.tag = parts[-1]
        entries = []
        for attrib in elem.attrib:
            if attrib.find(':') > -1:
                entries.append(attrib)
        for entry in entries:
            del elem.attrib[entry]

def attachments(root):
    responses = root.xpath('//Envelope/Body/mc_issue_getResponse/return')
    for response in responses:
        for elem in response.xpath('//attachments/item'):
            url = elem.xpath('download_url')[0].text
            pending = True
            retry = 0
            retries = 5
            while pending:
                try:
                    import urllib2
                    data = urllib2.urlopen(url)
                    if (data.getcode() < 400):
                        import base64
                        encoded = base64.b64encode(data.read())
                        import lxml.etree as etree
                        contents = etree.SubElement(elem, 'contents')
                        contents.text = encoded
                        pending = False
                    else:
                        raise RuntimeError('HTTP ERROR %d : %s' % { data.getcode(), data.geturl() })
                except e:
                    retry = retry + 1
                    if retry < retries:
                        # give some relief to the webserver
                        from time import sleep
                        sleep(5)
                    else:
                        raise e # RuntimeError('HTTP ERROR %d : %s' % { data.getcode(), data.geturl() })



def fatal(message):
    logging.critical(message)
    sys.exit(1)


class DebuggableObject(object):

    def debug(self, msg, *args, **kwargs):
        tag = self.debugtag()
        if tag:
            logging.debug('%s ' + msg, tag, *args, **kwargs)
        else:
            logging.debug(msg, *args, **kwargs)

    def debugtag(self):
        return ''


class MantisInterface(DebuggableObject):

    debug_enabled = False
    url = None
    user = None
    password = None
    include_open = False
    include_closed = False
    _client = None

    _enum = None
    _projects = None
    _open_issues = None
    _closed_issues = None
    _issue_map = None

    def debugtag(self):
        return 'Mantis'

    def read_config(self, cp):
        try:
            self.url = cp.get('mantis', 'url', False, os.environ)
        except ConfigParser.NoSectionError:
            pass
        except ConfigParser.NoOptionError:
            pass
        try:
            self.user = cp.get('mantis', 'user', False, os.environ)
        except ConfigParser.NoSectionError:
            pass
        except ConfigParser.NoOptionError:
            pass
        try:
            self.password = cp.get('mantis', 'password', False, os.environ)
        except ConfigParser.NoSectionError:
            pass
        except ConfigParser.NoOptionError:
            pass

    def url_base(self):
        if not self.url:
            fatal("missing Mantis URL")
        try:
            return self.url[:self.url.index('/api/')]
        except ValueError:
            return self.url

    def url_soap(self):
        return self.url_base() + '/api/soap/mantisconnect.php?wsdl'

    def url_issue(self, issue_id):
        return self.url_base() + '/view.php?id=%s' % issue_id

    def issue_link_markdown(self, mantis_issue_id):
        return '[mantis:' + '%07u' % mantis_issue_id + '](' + self.url_issue(mantis_issue_id) + ')'

    def extract_referred_mantis_issue_ids(self, text):
        r'''Return an iterator over the IDs of all Mantis issues that are referred in the given text
        using Mantis issue reference notation #N.
        '''
        for match in re.finditer(r'#(\d+)', text):
            yield int(match.group(1))

    def extract_linked_mantis_issue_ids(self, text):
        r'''Return an iterator over the IDs of all Mantis issues that are linked in the given text
        using full Mantis URLs.
        '''
        url_base = self.url_issue('')
        start = 0
        i = text.find(url_base, start)
        while i != -1:
            start = i + len(url_base)
            m = re.match('\d+\b', text[start:])
            if m:
                mantis_issue_id = int(m.group(0))
                yield mantis_issue_id
                start = + len(m.group(0))
            i = text.find(url_base, start)

    def rewrite_markdown_links(self, text, issue_linker):
        r'''In a supplied markdown text, rewrite links as created by self.issue_link_markdown() into
        other links whose markdown text is generated by passing the Mantis issue number to the
        supplied issue_linker() function.
        '''
        def rewrite(match):
            mantis_issue_id = int(match.group(1))
            return issue_linker(mantis_issue_id) if match.group(2) == self.url_issue(mantis_issue_id) else match.group(0)
        return re.subn(r'\[mantis:(\d{7})\]\(([^)]*)\)', rewrite, text)[0]

    def client(self):
        if not self._client:
            import suds
            url = self.url_soap()
            self.debug('create SOAP client, url=%r', url)
            self._client = suds.client.Client(url, retxml=False)
        return self._client

    def XXXuser_markdown(self, user):
        if not user:
            return 'None'
        mantis_user_url = self.url_base() + '/view_user_page.php?id=' + str(user.id)
        # Do not include the user's real name or email here, even though it is available via SOAP,
        # because we do not want to put people's email addresses in the clear on SCP to be harvested
        # by spammers.
        return '**[' + user.name + '](' + mantis_user_url + ')**'

    def service(self, method, exception_fatal=True, **kwargs):
        '''This method exists to create a single code path to invoking SOAP services, that can be
        logged.
        '''
        safe_kwargs = dict(kwargs)
        if 'password' in safe_kwargs:
            safe_kwargs['password'] = '***'
        import suds
        try:
            client = self.client()
            self.debug('%s(%s)', method, ', '.join('%s=%s' % i for i in safe_kwargs.iteritems()))
            return getattr(client.service, method)(**kwargs)
        except suds.WebFault, e:
            if self.debug:
                print >>sys.stderr, '%s(%s)' % (method, ', '.join('%s=%r' % i for i in kwargs.iteritems()))
                traceback.print_exc()
            if not exception_fatal:
                raise
            fatal(e)

    def service_cred(self, method, **kwargs):
        _kwargs = dict(self.credentials())
        _kwargs.update(kwargs)
        return self.service(method, **_kwargs)

    def credentials(self):
        if self.user is None:
            fatal("missing Mantis user name")
        if self.password is None:
            fatal("missing Mantis password")
        return {'username': self.user, 'password': self.password}

    def get_enum(self, enum, name=None, **kwopts):
        if self._enum is None:
            self._enum = {}
        if enum not in self._enum:
            self._enum[enum] = {}
            for elt in self.service_cred('mc_enum_' + enum):
                self._enum[enum][elt.name] = elt
        if name is None:
            return self._enum[enum].values()
        if name not in self._enum[enum]:
            fatal('no name %r in Mantis %r enum' % (name, enum))
        return self._enum[enum][name]

    def get_enum_status(self, name=None, **kwopts):
        return self.get_enum('status', name, **kwopts)

    def get_enum_resolutions(self, name=None, **kwopts):
        return self.get_enum('resolutions', name, **kwopts)

    def get_users(self, project_ids=None, **kwopts):
        if not project_ids:
            project_ids = []
            projects = self.service_cred('mc_projects_get_user_accessible', **kwopts)
            for project in projects:
                project_ids.append(project.id)
        all_users = {}
        for project_id in project_ids:
            users = self.service_cred('mc_project_get_users', project_id=project_id, access=1, **kwopts)
            for user in users:
                all_users[user.id] = user
        return all_users

    def get_projects(self, **kwopts):
        if self._projects is None:
            self._projects = {}
            projects = self.service_cred('mc_projects_get_user_accessible', **kwopts)
            for project in projects:
                self._projects[project.id] = project
        return self._projects

    def get_issue_asXML(self, mantis_issue_id):
        # this call obtains an object, which we discard ...
        obj = self.get_issue(mantis_issue_id)
        # .. because we are actually interested on the XML backing it
        xml = self.client().last_received().plain()
        return xml

    def get_issue(self, mantis_issue_id):
        for idict in self._open_issues, self._closed_issues:
            if idict and mantis_issue_id in idict:
                return idict[mantis_issue_id]
        import suds
        try:
            mantis_issue = self.service_cred('mc_issue_get', issue_id=mantis_issue_id, exception_fatal=False)
        except suds.WebFault:
            return None
        if mantis_issue.status.name in ('resolved', 'closed'):
            if self._closed_issues is None:
                self._closed_issues = {}
            self._closed_issues[mantis_issue_id] = mantis_issue
        else:
            if self._open_issues is None:
                self._open_issues = {}
            self._open_issues[mantis_issue_id] = mantis_issue
        return mantis_issue

    def get_open_issues(self, project_ids=None, per_page=100, **kwopts):
        if self._open_issues is None:
            self._open_issues = {}
            if not project_ids:
                project_ids = self.get_projects(**kwopts).keys()
            for project_id in project_ids:
                if project_id not in self._open_issues:
                    self._open_issues[project_id] = {}
                    page = 1
                    while True:
                        issues = self.service_cred('mc_project_get_issues', project_id=project_id, page_number=page, per_page=per_page, **kwopts)
                        for issue in issues:
                            self._open_issues[project_id][issue.id] = issue
                        if len(issues) < per_page:
                            break
                        page += 1
        ret = dict()
        for project_id in project_ids or self._open_issues.keys():
            ret.update(self._open_issues[project_id])
        return ret

    def get_closed_issues(self, project_ids=None, **kwopts):
        if self._closed_issues is None:
            self._closed_issues = {}
            if not project_ids:
                project_ids = self.get_projects(**kwopts).keys()
            import suds
            max_id = 0
            for project_id in project_ids:
                max_id = max(max_id, self.service_cred('mc_issue_get_biggest_id', project_id=project_id, **kwopts))
            open_issues = self.get_open_issues(project_ids, **kwopts)
            for id in xrange(1, max_id + 1):
                if id not in open_issues:
                    try:
                        issue = self.service_cred('mc_issue_get', issue_id=id, exception_fatal=False, **kwopts)
                        self._closed_issues[issue.id] = issue
                    except suds.WebFault:
                        pass
        ret = dict()
        for issue_id, issue in self._closed_issues.iteritems():
            if project_ids is None or issue.project.id in project_ids:
                ret[issue_id] = issue
        return ret

    def get_issues(self, project_ids=None, **kwopts):
        ret = dict()
        if self.include_open or not self.include_closed:
            ret.update(self.get_open_issues(project_ids, **kwopts))
        if self.include_closed or not self.include_open:
            ret.update(self.get_closed_issues(project_ids, **kwopts))
        return ret

    def _invalidate_issue(self, mantis_issue_id):
        try:
            del self._open_issues[mantis_issue_id]
        except (TypeError, KeyError):
            pass
        try:
            del self._closed_issues[mantis_issue_id]
        except (TypeError, KeyError):
            pass

    def XXXextract_issue_references(self, mantis_issue_id):
        r'''Return an iterator over all references to other issues in the text, relationships and
        notes of the given Mantis issue.  Each returned reference may be an int to indicate another
        Mantis issue id, or a ScpIssueRef to indicate a SCP issue.
        '''
        mantis_issue = self.get_issue(mantis_issue_id)
        if mantis_issue is not None:
            if hasattr(mantis_issue, 'relationships') and mantis_issue.relationships:
                for rel in mantis_issue.relationships:
                    if rel.type.name == 'related to':
                        yield rel.target_id
            texts = [mantis_issue.description]
            if hasattr(mantis_issue, 'steps_to_reproduce') and mantis_issue.steps_to_reproduce:
                texts.append(mantis_issue.steps_to_reproduce)
            if hasattr(mantis_issue, 'additional_information') and mantis_issue.additional_information:
                texts.append(mantis_issue.additional_information)
            if hasattr(mantis_issue, 'notes') and mantis_issue.notes:
                texts += (note.text for note in mantis_issue.notes if note.text)
            for text in texts:
                for ref in ScpInterface.extract_issue_links(text):
                    yield ref
                for id in self.extract_referred_mantis_issue_ids(text):
                    yield id
                for id in self.extract_linked_mantis_issue_ids(text):
                    yield id

    MIGRATION_TEXT = 'This issue is now being tracked on SCP: '

    def XXXmigrated_scp_references(self, mantis_issue):
        r'''Return an iterator of ScpIssueRef objects indicating the SCP issues to which this
        Mantis issue is marked has having been migrated.  This does not check that the SCP issues
        are consistent, ie, are not deleted and are marked has having originated from the same
        Mantis issue.
        '''
        if hasattr(mantis_issue, 'notes') and mantis_issue.notes:
            for note in mantis_issue.notes:
                ref = self.migrated_scp_reference(note=note)
                if ref:
                    yield ref

    def XXXmigrated_scp_reference(self, issue=None, note=None, text=None):
        '''Return a ScpIssueRef indicating the SCP issue to which this Mantis issue has
        already been migrated.
        '''
        if text is not None:
            text = text.lstrip()
            if text.startswith(self.MIGRATION_TEXT):
                try:
                    return ScpInterface.parse_issue_url(text[len(self.MIGRATION_TEXT):].split()[0])
                except (IndexError, ValueError): pass
            return None
        elif note is not None:
            return self.migrated_scp_reference(text= note.text if hasattr(note, 'text') and note.text else '')
        else:
            refs = list(self.migrated_scp_references(issue))
            return refs[-1] if refs else None

    def add_note(self, mantis_issue_id, note_text):
        note = self.client().factory.create('IssueNoteData')
        note.text = note_text
        self.service_cred('mc_issue_note_add', issue_id=mantis_issue_id, note=note)
        self._invalidate_issue(mantis_issue_id)

    def update_status(self, mantis_issue_id, status=None, resolution=None):
        mantis_issue = self.get_issue(mantis_issue_id)
        self._invalidate_issue(mantis_issue_id)
        if mantis_issue is not None:
            if status:
                mantis_issue.status = self.get_enum_status(status)
            if resolution:
                mantis_issue.resolution = self.get_enum_resolutions(resolution)
            return self.service_cred('mc_issue_update', issueId=mantis_issue_id, issue=mantis_issue)


class Context(DebuggableObject):
    debug_enabled = False
    dry_run = False
    no_close_mantis = False
    opts = None
    user_map = ()
    _issue_map = None

    mantis = MantisInterface()

    def read_config_file(self):
        path = self.config_path
        if os.path.exists(path):
            stat = os.stat(path)
            if stat.st_uid != os.getuid():
                logging.warn("%s exists but is owned by uid %s (should be %s) -- ignored" % (path, stat.st_uid, getuid()))
            elif stat.st_mode & 0177:
                logging.warn("%s exists but has mode %#o (should be at most 0600) -- ignored" % (path, stat.st_mode & 0777))
            else:
                cp = ConfigParser.SafeConfigParser()
                cp.optionxform = str
                cp.readfp(file(path))
                self.mantis.read_config(cp)
                self.user_map = {}
                try:
                    for key, value in cp.items('user map'):
                        self.user_map[key] = cp.get('user map', key, False, os.environ)
                except ConfigParser.NoSectionError:
                    pass

    def XXXmap_user(self, mantis_user):
        '''Convert a Mantis AccountData object into a SCP NamedUser object.'''
        if mantis_user is None:
            return None
        login = self.user_map.get(mantis_user.name, None)
        if not login:
            return None
        return self.scp.main().open().get_user(login)

    def XXXresolve_user(self, mantis_account):
        '''Convert a Mantis AccountData object into a SCP AuthenticatedUser object, plus some
        text that can be used to link to the user.
        '''
        login = self.user_map.get(mantis_account.name)
        ghc, ref = None, None
        if login is None:
            ref = self.mantis.user_markdown(mantis_account)
            self.debug('mantis user %r does not resolve to SCP user', mantis_account.name)
        else:
            ref = '@' + login
            ghc = self.scp.connection(login)
            self.debug('resolved mantis user %r to SCP %r %s', mantis_account.name, ref, '(auth)' if ghc else '(no auth)')
        return ghc, ref

    def XXXmantis_issue_refs(self, mantis_issue_id, target_issue_ref=None):
        r'''Return an interator over references for the given Mantis issue.  If the issue has been
        migrated to any SCP issues (other than the target issue), then this will iterate over one
        or more ScpIssueRef objects (excluding the target issue).  Otherwise, it will iterate
        over a single int, which is the Mantis issue number.
        '''
        scp_refs = list(self.mantis_scp_issue_refs(mantis_issue_id))
        try: scp_refs.remove(target_issue_ref)
        except ValueError: pass
        if scp_refs:
            for ref in scp_refs:
                yield ref
        else:
            yield mantis_issue_id

    def XXXmantis_issue_link_markdown(self, mantis_issue_id, target_issue_ref=None, linkset=None):
        r'''Return an iterator over markdown references for the given Mantis issue.  If the issue
        has been migrated to any SCP issues, then this will iterate over SCP Flavoured
        Markdown references to those SCP issues.  Otherwise, it will return a standard Markdown
        link to the Mantis issue itself.
        '''
        for ref in self.mantis_issue_refs(mantis_issue_id, target_issue_ref=target_issue_ref):
            linkset.add(ref)
            yield ref.markdown(target_issue_ref) if isinstance(ref, ScpIssueRef) else self.mantis.issue_link_markdown(mantis_issue_id)

    def XXXmantis_scp_issue_refs(self, mantis_issue_id):
        r'''Return an iterable over all SCP references to which a given Mantis issue has been
        migrated.  It does not return references to SCP issues that are marked as deleted or
        which are inconsistent.  Ie, the only SCP issues returned are those which are marked
        as having originated from the given Mantis issue.
        '''
        if self._issue_map is None:
            self._issue_map = {}
        if mantis_issue_id not in self._issue_map:
            mantis_issue = self.mantis.get_issue(mantis_issue_id)
            refs = []
            if mantis_issue is not None:
                for ref in self.mantis.migrated_scp_references(mantis_issue):
                    issue = self.scp.default_connection().issue(ref)
                    if not issue.is_deleted() and issue.is_migrated_from(self.mantis, mantis_issue_id):
                        refs.append(ref)
            self._issue_map[mantis_issue_id] = refs
        return iter(self._issue_map[mantis_issue_id])

    def XXXadd_mantis_scp_issue_ref(self, mantis_issue_id, ref):
        r'''Add the given SCP issue ref to the list of issues to which the given Mantis issue
        has been Migrated.
        '''
        if ref not in self.mantis_scp_issue_refs(mantis_issue_id):
            self._issue_map[mantis_issue_id].append(ref)

    def XXXrelink_markdown(self, text, scp_issue_ref, linkset=None):
        r'''In the given markdown test, replace all links to migrated Mantis issues with their
        equivalent SCP reference, except for those which have been migrated to a given target
        SCP issue.
        '''
        return self.mantis.rewrite_markdown_links(text, lambda id: ' '.join(self.mantis_issue_link_markdown(id, scp_issue_ref, linkset=linkset)))

    def escape_markdown(self, text):
        return re.subn(r'[\\`*_{}\[\]()#+\-.!]', r'\\\g<0>', text)[0]

    def XXXtext_to_markdown(self, text, target_issue_ref=None, linkset=None):
        # Remove leading blank lines.
        text = re.sub(r'^( *\n)+', '', text)
        # If it looks like a stack trace or log file, then preformat it.  Otherwise, remove
        # unintended Markdown effects.
        if (    len(re.findall(r'\bat .*\(.*\.java:[0-9]+\)', text)) >= 3
            or  len(re.findall(r'^ *(DEBUG|WARN|INFO|ERROR):', text, flags=re.MULTILINE)) >= 3
            or  len(re.findall(r'^ *[EWIDV]/', text, flags=re.MULTILINE)) >= 3
            ):
            text = '```\n' + text + '\n```'
        else:
            # Remove trailing newlines and blank lines.
            text = text.rstrip()
            # Reduce indents or four or more spaces to three spaces, to avoid
            # them being formatted as code.
            text = re.subn(r'^ {4,}', '   ', text, flags=re.MULTILINE)[0]
            # Convert Mantis issue references (#N) into links to Mantis links.
            text = re.subn(r'#(\d+)', lambda match: ' '.join(self.mantis_issue_link_markdown(int(match.group(1)), target_issue_ref, linkset=linkset)), text)[0]
            # Convert SCP issue links to references.
            if target_issue_ref:
                def replace_link(match):
                    ref = ScpIssueRef(match.group(1), match.group(2), int(match.group(3)))
                    if linkset is not None:
                        linkset.add(ref)
                    return ref.markdown(target_issue_ref)
                text = re.subn(r'\bhttps?://github.com/([^\s/]+)/([^\s/]+)/issues/(\d+)\b', replace_link, text)[0]
        # Convert links to already-migrated Mantis issues to their equivalent references to SCP
        # issues.
        def make_link(mantis_issue_id):
            return ' '.join(self.mantis_issue_link_markdown(mantis_issue_id, target_issue_ref, linkset=linkset))
        text = self.mantis.rewrite_markdown_links(text, make_link)
        return text

    def XXXparse_issue_reference(self, text):
        r'''Parse the given string as either a ScpIssueRef "repo#number" or
        an int (Mantis issue id).
        '''
        m = re.match(r'([^/#]+)#(\d+)$', text)
        if m:
            repo_name = m.group(1)
            scp_issue_number = int(m.group(2))
            if scp_issue_number > 0:
                return self.scp.default_connection().org().repo(repo_name).issue_ref(scp_issue_number)
        else:
            mantis_issue_id = int(text)
            if mantis_issue_id > 0:
                return mantis_issue_id
        raise ValueError(text)

    def XXXrelink(self, todo, repo_ref=None):
        r'''Given an iterable over various objects: ScpIssueRef, ScpIssue and int (Mantis
        issue id), re-link all the body and comment texts of them and all related SCP issues.
        '''
        todo = set(todo)
        done = set()
        while todo:
            self.debug('relink todo = %s', ' '.join(str(obj) if isinstance(obj, int) else obj.markdown(repo_ref) for obj in todo))
            obj = todo.pop()
            if isinstance(obj, ScpIssueRef):
                obj = self.scp.default_connection().issue(obj)
            if isinstance(obj, ScpIssue):
                assert obj.ref not in done
                done.add(obj.ref)
                more_todo = set()
                self.relink_scp_issue(obj, more_todo)
                todo |= more_todo - done
            else:
                done.add(obj)
                assert isinstance(obj, int)
                todo |= set(self.mantis.extract_issue_references(obj)) - done

    def XXXrelink_scp_issue(self, issue, linkset=None):
        r'''Relink all the body and comment texts in the given SCP issue.
        '''
        issue.debug('relink')
        if issue.open() is not None:
            body = self.relink_markdown(issue.open().body, issue.ref, linkset=linkset)
            if body != issue.open().body:
                issue.edit(body=body, dry_run=self.dry_run)
            if issue.open().comments:
                issue.debug('get_comments()')
                for comment in issue.open().get_comments():
                    if not comment.body.startswith(ScpIssue.MIGRATION_TEXT):
                        body = self.relink_markdown(comment.body, issue.ref, linkset=linkset)
                        if body != comment.body:
                            issue.debug('comment=%r edit(body=%r)', comment.id, body)
                            if not self.dry_run:
                                comment.edit(body=body)

if __name__ == '__main__':
    main()
