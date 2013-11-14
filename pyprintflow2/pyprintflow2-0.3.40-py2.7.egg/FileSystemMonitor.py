'''
Created on Sep 9, 2013

@author: "Colin Manning"
'''

import os.path
import pyinotify
import requests
import uuid
import time
import traceback
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from JDs import JDs
from PdfToolbox import PdfToolbox
import utils
import nooshsoap

COMMASPACE = ', '    

class FileSystemMonitor(pyinotify.ProcessEvent):
    
    WORKGROUP_CLASS = 'workgroup'
    PROJECT_CLASS = 'project'
    SPECIFICATION_CLASS = 'specification'
    FILE_CLASS = 'file'
    USER_CLASS = 'user'

    #watch_mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE # watched events
    CREATE_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CREATE']
    CLOSE_WRITE_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CLOSE_WRITE']
    MOVED_FROM_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_MOVED_FROM']
    MOVED_TO_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_MOVED_TO']
    DELETE_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_DELETE']
    watch_mask = CREATE_EVENT | CLOSE_WRITE_EVENT | MOVED_FROM_EVENT | MOVED_TO_EVENT | DELETE_EVENT
    
    ignore_files = ['New folder', '.DS_Store', 'untitled folder', 'approved', 'failed', '.dropbox']
    
    created_files = {}
    modified_files = {}
    wdd = None
    wm = None
    notifier = None
    workgroup = {}
    watch_dir = ''
    cumulus_api_url = ''
    cumulus_baseurl = ''
    noosh_api = {}
    pdftoolbox_path = ''
    access_token = ''
    db_dir = ''
    jds = None
    logger = None
    pdf_toolbox = None
    mailer = None
    mail_signature_logo = None
    company_web_address = None
    os_userid = None
    os_groupid = None
    noosh_soap_api = None
    
    config_data = None
    web_rootdir = None
    web_baseurl = None
    ready = False
    running = False
    
    def _ignore_file(self, name):
        return name in self.ignore_files
    
    def __init__(self, config_file, workgroup_id):
        pyinotify.ProcessEvent.__init__(self)
        self.config_data = config_file
        self.logger = logging.getLogger('printflow2')
        if os.path.exists(config_file):
            with open(config_file) as f:
                self.config_data = json.load(f)
                f.close()
            self.noosh_api = self.config_data['nooshapi']
            self.noosh_soap_api = self.config_data['noosh_soap_api']
            self.cumulus_api_url = self.config_data['cumulusapi']
            self.cumulus_baseurl = self.config_data['cumulusbaseurl']
            self.access_token = self.config_data['accesstoken']
            self.pdftoolbox_path = self.config_data['pdftoolbox']
            self.db_dir = self.config_data['dbdir']
            self.web_rootdir = self.config_data['web_server']['rootdir']
            self.web_baseurl = self.config_data['web_server']['baseurl']
            
            self.jds = JDs(self.db_dir, self.os_userid, self.os_groupid)
            self.jds.register_class(self.WORKGROUP_CLASS)
            self.jds.register_class(self.PROJECT_CLASS)
            self.jds.register_class(self.SPECIFICATION_CLASS)
            self.jds.register_class(self.FILE_CLASS)
            self.jds.register_class(self.USER_CLASS)
            self.workgroupId = workgroup_id
            self.workgroup = self.jds.fetch(self.WORKGROUP_CLASS, self.workgroupId)
            self.watch_dir = self.workgroup['dropbox_root']
            self.os_userid = self.workgroup['os_userid']
            self.os_groupid = self.workgroup['os_groupid']
                        
            self.mail_server = self.config_data['mail_server']
            self.setup_mailer(self.mail_server)
            self.company_web_address = self.config_data['company_web_address']
            
            self.pdf_toolbox = PdfToolbox(self.config_data['pdftoolbox'], \
                                          self.config_data['pdftoolbox_cache_path'], 
                                          self.config_data['activationcode'], \
                                          self.config_data['pdftoolbox_tmpdir'], \
                                          self.web_rootdir)
            self.wm = pyinotify.WatchManager()
            #self.wdd = self.wm.add_watch(self.watch_dir, self.watch_mask, rec=True, auto_add=True)
            self.ready = True
        else:
            self.ready = False
            print "Failed to load config file: ", config_file
            
    def scanFolders(self):
        # check to see if there are unprocessed files in the monitored folder
        # stop the monitor, check for files, and then restart it - do this every few minutes
        #if self.running:
            #self.stop()
        try:
            self.logger.info("Scanning" + str(self.watch_dir) + " for unprocessed files")
            self.walk(self.watch_dir)
        except:
            self.logger.error('Problem scanning folders'+self.scan_check_interval+' seconds.')
        #finally:
            #self.start()

    def walk(self, f):
        # ok here we do the walk
        for dirname, dirnames, filenames in os.walk(f):
            # print path to all subdirectories first.
            #for subdirname in dirnames:
            #    print os.path.join(dirname, subdirname)

            # print path to all filenames.
            for filename in filenames:
                # if file in folder other than failed or approved, then may not have been to be processed
                parent_dir = dirname.split('/')[-1]
                filename_bits = filename.split('.')
                if (parent_dir == 'approved') or (parent_dir == 'failed') or (parent_dir == 'MisplacedFiles') \
                    or (filename[0] == '.') or ((filename[0] == '_') or (len(filename_bits) > 1 and filename_bits[-1] == 'json') ):
                    continue
                pathname = os.path.join(dirname, filename)
                path_bits = dirname.split('/')
                try:
                    self.process_file(dirname, filename, pathname)
                    '''
                    if (len(path_bits) >=3 and path_bits[-3] == 'Projects'):
                        self.logger.info("found unprocessed file: "+pathname+' processing now')
                        self.process_file(dirname, filename, pathname)
                    else:
                        self.process_spurious_file(dirname, filename, pathname)
                        #os.remove(pathname)
                    '''
                except:
                    self.logger.error('problem processing file')            
                    traceback.print_exc()
            
    def start(self):
        if self.ready:
            self.wdd = self.wm.add_watch(self.watch_dir, self.watch_mask, rec=True, auto_add=True)
            self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
            self.notifier.start()
            self.running = True
        
    def stop(self):
        if self.running:
            self.wm.rm_watch(self.watch_dir, rec=True)
            self.running = False
                
    def setup_mailer(self, mail_server):
        self.mailer = smtplib.SMTP(mail_server['host'], mail_server['port'])
        self.mail_signature_logo = mail_server['signature_logo']
        try:
            self.mailer.login(mail_server['default_login'], mail_server['default_password'])
        except:
            self.logger.error('Failed to login to mail server')
        
    def send_mail(self, receivers, subject, message):
        try:
            send_message = MIMEText(message, 'plain')
            send_message['Subject'] = subject
            send_message['From'] = self.mail_server['default_login']
            send_message['To'] = COMMASPACE.join(receivers)
            try:
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
            except:
                # assume mailserver died, login again and retry
                self.setup_mailer(self.mail_server)
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
        except:
            self.logger.error('problem sending plain text email')            
            traceback.print_exc()
                
    def send_html_mail(self, receivers, subject, message):
        try:
            send_message = MIMEText(message.encode('utf-8'), 'html', 'utf-8')
            send_message['Subject'] = Header(subject, 'utf-8')
            send_message['From'] = self.mail_server['default_login']
            send_message['To'] = COMMASPACE.join(receivers)
            try:
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
            except:
                # assume mailserver died, login again and retry
                self.setup_mailer(self.mail_server)
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
        except:
            self.logger.error('problem sending html email')            
            traceback.print_exc()
            
            
    def is_ready(self):
        return self.ready
            
    def process_IN_CREATE(self, event):
        # could have been processed already
        if os.path.exists(event.pathname):
            self.process_file(event.path, event.name, event.pathname)
        
    def process_IN_MODIFY(self, event):
        self.process_file(event.path, event.name, event.pathname)
    
    # we get this when a file is changed and closed in the folder directly
    def process_IN_CLOSE_WRITE(self, event):
        if self._ignore_file(event.name):
            return
        
        # could have been processed already
        if os.path.exists(event.pathname):
            self.process_file(event.path, event.name, event.pathname)

    # we seem to get this when file deleted form network folder (e.g. Dropbox)
    def process_IN_MOVED_FROM(self, event):
        if self._ignore_file(event.name):
            return

    def process_IN_MOVED_TO(self, event):
        self.process_file(event.path, event.name, event.pathname)
        
    def process_spurious_file(self, file_path, file_name, file_pathname):
        if self._ignore_file(file_name):
            return
        path_bits = file_path.split('/')
        if path_bits[-1] == 'approved':
            return
        if path_bits[-1] == 'failed':
            return
        if (file_name[-1] == 'json') or (file_name[0] == '.') or ((file_name[0] == '_')):
            return
        
        self.logger.info("processing spurious file: "+ file_pathname)       
        try:
            path_bits = file_path.split('/')
            # lets see if we can find a client name in the path, if so notify the client
            #result['dropbox_path'] = workgroup['dropbox_root'] + '/' + project['client_account'] +"/Projects/" + str(project['project_id'])
            for index in range(len(path_bits)-1, 0, -1):
                client_name = None
                if path_bits[index] in self.workgroup['clients']:
                    client_name = path_bits[index]
                elif path_bits[index] == 'Projects' and index > 0:
                    client_name = path_bits[index-1]
                elif index == 0:
                    client_name = path_bits[0]
                if client_name is not None:  
                    try:
                        client = self.workgroup['clients'][client_name]
                        misplacedFilesPath = self.workgroup['dropbox_root'] + '/' + client_name +"/MisplacedFiles"
                        utils.ensureDirectoryExistsForUser(misplacedFilesPath, self.os_userid, self.os_groupid, 0o755)
                        utils.safe_file_move(file_pathname, misplacedFilesPath)
                        file_sub_path = ''
                        st = False
                        for si in range(len(path_bits)):
                            if path_bits[si] == client_name:
                                st = True
                            if not st:
                                continue
                            file_sub_path += '/' + path_bits[si]
                        if 'flowdock_accesstoken' in client:
                            self.inform_flowdock_spurious(client['flowdock_accesstoken'], client_name, file_sub_path, file_name)
                        else:
                            subject = 'Oops file ' + file_name + ' incorrectly uploaded for ' + client_name
                            message = self.get_email_spurious_body(client_name, file_sub_path, file_name)
                            message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)
                            mail_list = client['account_manager_emails']
                            for fi in range(len(client['file_notify_emails'])):
                                if client['file_notify_emails'][fi] not in mail_list:
                                    mail_list.append(client['file_notify_emails'][fi])
                            self.send_html_mail(mail_list, subject, message)

                    except:
                        # nothing to do
                        break
                    break
        except:
            self.logger.error('Problem processing spuriousfile: '+file_pathname)
            traceback.print_exc()
            # lets see if we can find a client
        
    # file created over network (e.g. Dropbox)
    def process_file(self, file_path, file_name, file_pathname):
        if os.path.isdir(file_pathname):
            return
        if self._ignore_file(file_name):
            return
        path_bits = file_path.split('/')
        parent_dir = path_bits[-1]
        filename_bits = file_name.split('.')
        if (parent_dir == 'approved') or (parent_dir == 'failed') or (parent_dir == 'MisplacedFiles') \
            or (file_name[0] == '.') or ((file_name[0] == '_') or (len(filename_bits) > 1 and filename_bits[-1] == 'json') ):
            return
        
        try:
            is_spurious_file = False
            guid = str(uuid.uuid4())
            path_bits = file_path.split('/')
            #project = self.jds.fetch(self.PROJECT_CLASS, path_bits[-2])
            specification = self.jds.fetch(self.SPECIFICATION_CLASS, path_bits[-1])
            if specification is None:
                is_spurious_file = True
            else:
                project = self.jds.fetch(self.PROJECT_CLASS, specification['id_project'])
                if project is None:
                    is_spurious_file = True
            if is_spurious_file:
                self.process_spurious_file(file_path, file_name, file_pathname)
                return
            
            # ok, we should be good to go
            workgroup = self.jds.fetch(self.WORKGROUP_CLASS, project['id_parent'])
            #client = workgroup['clients'][project['noosh_project']['client_account']]            
            client = None
            project_details = project['noosh_project']
            if ('client_account' in project_details and project_details['client_account'] is not None) and \
                project_details['client_account'] in workgroup['clients'] and \
                'users' in workgroup['clients'][project_details['client_account']]:
                client = workgroup['clients'][project_details['client_account']]
            elif 'identify_filter_key' in workgroup and 'custom_fields' in project_details:
                k = workgroup['identify_filter_key']
                for custom_field in project_details['custom_fields']:
                    if client is not None:
                        break
                    if k == custom_field['param_name']:
                        if custom_field['string_value'] is not None:
                            v = custom_field['string_value']
                        elif custom_field['number_value'] is not None:
                            v = custom_field['number_value']
                        for a_client_name in workgroup['clients']:
                            a_client = workgroup['clients'][a_client_name]
                            if 'identify_filter_value' in a_client and a_client['identify_filter_value'] == v:
                                client = a_client
                                break            
            status, info, output, report_folder, report_file_mask, report_file_text, report_file_html = self.preflight_check(file_path, file_name, file_pathname, project, specification, guid)
            db_file_path = None
            db_file = None
            proj = None
            spec = None
            #uploaded_by = file_path.split('/')[-2]
            uploaded_by = file_path.split('/')[-3]
            if status:
                approved_path = os.path.join(file_path, "approved")
                utils.ensureDirectoryExistsForUser(approved_path, self.os_userid, self.os_groupid, 0o755)
                # status 2 => "Available" in catalog PF Status field
                db_file, db_file_path = self.upload_file_to_cumulus(client, file_path, file_name, file_pathname, project, specification, '2', info, output, guid, \
                                                                  report_file_mask, report_file_text, report_file_html, uploaded_by)
                proj = project['noosh_project']
                spec = specification['noosh_specification']
                subject = 'File uploaded for ' + proj['client_account'] + ' - Project ' +proj['project_name'] + ' (' + str(proj['project_id'])+')'
                message = self.get_email_file_uploaded_body(project, specification, db_file)
                message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)            
                mail_list = client['account_manager_emails']
                for fi in range(len(client['file_notify_emails'])):
                    if client['file_notify_emails'][fi] not in mail_list:
                        mail_list.append(client['file_notify_emails'][fi])
                self.send_html_mail(mail_list, subject, message)
                if 'flowdock_accesstoken' in workgroup['clients'][proj['client_account']]:
                    self.inform_flowdock_uploaded(workgroup['clients'][proj['client_account']]['flowdock_accesstoken'], proj, spec, db_file)
            else:
                proj = project['noosh_project']
                spec = specification['noosh_specification']
                db_file, db_file_path = self.register_failed_file(file_path, file_name, file_pathname, project, specification, status, info, output, guid, \
                                                                  report_file_mask, report_file_text, report_file_html, uploaded_by)
                subject = 'File rejected for ' + proj['client_account'] + ' - Project ' +proj['project_name'] + ' (' + str(proj['project_id'])+')'
                message = self.get_email_file_rejected_body(proj, spec, db_file)
                message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)            
                mail_list = client['account_manager_emails']
                for fi in range(len(client['file_notify_emails'])):
                    if client['file_notify_emails'][fi] not in mail_list:
                        mail_list.append(client['file_notify_emails'][fi])
                self.send_html_mail(mail_list, subject, message)
                self.logger.info('pre-flight check failed file: ' + file_pathname)
                if 'flowdock_accesstoken' in workgroup['clients'][proj['client_account']]:
                    self.inform_flowdock_rejected(workgroup['clients'][proj['client_account']]['flowdock_accesstoken'], proj, spec, db_file)
            self.build_file_web_page(proj, spec, db_file)        

        except:
            self.logger.error('Problem processing file: '+file_pathname)
            self.process_spurious_file(file_path, file_name, file_pathname)
            traceback.print_exc()

    # we seem to get this on directory delete, but not file delete, if file is network (e.g. Dropbox)
    def process_IN_DELETE(self, event):
        if self._ignore_file(event.name):
            return
        
        self.logger.info("Delete:" + str(event))
        #pathname = os.path.join(event.path, event.name)
        
    def inform_flowdock_uploaded(self, accesstoken, proj, spec, db_file):
        subject = 'File uploaded for ' + proj['client_account'] + ' - Project ' +proj['project_name'] + ' (' + str(proj['project_id'])+')'
        message = (' \
<h3>A file has been uploaded for "%s"</h3> \
<div id="wrap" style="border-top-style:solid;border-top-width:1px;border-top-color:#666666;border-bottom-style:solid;border-bottom-width:1px;border-bottom-color:#666666">\
<div style="float:left;margin: 15 15 15 15"> \
<table> \
<tr><td>Client:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Reference:</td><td>%s</td></tr> \
<tr><td>Original File Name:</td><td>%s</td></tr> \
<tr><td>Production Name:</td><td>%s</td></tr> \
<tr><td>Size:</td><td>%s bytes</td></tr> \
<tr><td>Upload Time:</td><td>%s</td></tr> \
<tr><td>Pre-flight Status:</td><td>%s</td></tr> \
<tr><td>View pre-flight report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
</table></div> \
<div style="float: left;margin-bottom:15;margin-top:15;border-style:solid;border-width:1px;border-color:#666666"> \
<div style="margin:15 15 15 15"><a href="%s"><img src="%s"></a></div></div><br style="clear:both" /></div>'
            % (spec['spec_name'], proj['client_account'], proj['project_name'], str(proj['project_id']), \
               spec['spec_name'], str(spec['spec_id']), str(spec['reference_number']),\
               db_file['original_name'], db_file['dam_name'], str(db_file['size']), utils.parse_time(db_file['upload_time'], \
               utils.STYLE_DATE_TIME_SHORT_MONTH), db_file['preflight_info'], \
               db_file['preflight_report_html'], \
               db_file['download_url'], db_file['thumbnail_url']))
        post_url = 'https://api.flowdock.com/v1/messages/team_inbox/' + accesstoken
        
        data =  { "source": "PrintFlow 2 Service", "from_address" : "colin@printoutsource.com", \
                    "subject": subject, "content" : message, \
                    "project": str(proj['project_id']), \
                    "tags": ["@all", "#project", str(proj['project_id']), str(spec['spec_id']), str(db_file['original_name'])] }
        d = json.dumps(data)
        headers = { "Content-Type": "application/json" }
        response = requests.post(post_url, data=d, headers=headers)
        if response.status_code == 200:
            # now link to category
            r = response.json()

        
    def inform_flowdock_rejected(self, accesstoken, proj, spec, db_file):
        subject = 'File rejected for ' + proj['client_account'] + ' - Project ' +proj['project_name'] + ' (' + str(proj['project_id'])+')'
        message = (' \
<h3>A file has been rejected for "%s"</h3> \
<div id="wrap" style="border-top-style:solid;border-top-width:1px;border-top-color:#666666;border-bottom-style:solid;border-bottom-width:1px;border-bottom-color:#666666">\
<div style="float:left;margin: 15 15 15 15"> \
<table> \
<tr><td>Client:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Reference:</td><td>%s</td></tr> \
<tr><td>Original File Name:</td><td>%s</td></tr> \
<tr><td>Production Name:</td><td>%s</td></tr> \
<tr><td>Size:</td><td>%s bytes</td></tr> \
<tr><td>Upload Time:</td><td>%s</td></tr> \
<tr><td>Pre-flight Status:</td><td>%s</td></tr> \
<tr><td>View HTML Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View Text_Report Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View PDF Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
</table> \
</div> \
<div style="float: left;margin-bottom:15;margin-top:15;border-style:solid;border-width:1px;border-color:#666666"> \
<div style="margin:15 15 15 15"><a href="%s"><img src="%s"></a></div> \
</div><br style="clear:both" /></div>' \
            % (spec['spec_name'], proj['client_account'], proj['project_name'], str(proj['project_id']), \
               spec['spec_name'], str(spec['spec_id']), str(spec['reference_number']),\
               db_file['original_name'], db_file['dam_name'], str(db_file['size']), \
               utils.parse_time(db_file['upload_time'], utils.STYLE_DATE_TIME_SHORT_MONTH), db_file['preflight_info'], \
               db_file['preflight_report_html'], db_file['preflight_report_text'], db_file['preflight_report_mask'], \
               db_file['preflight_report_html'], db_file['thumbnail_url']))
        post_url = 'https://api.flowdock.com/v1/messages/team_inbox/' + accesstoken
        
        data =  { "source": "PrintFlow 2 Service", "from_address" : "colin@printoutsource.com", \
                    "subject": subject, "content" : message, \
                    "project": str(proj['project_id']), \
                    "tags": ["@all", "#project", str(proj['project_id']), str(spec['spec_id'])] }
        d = json.dumps(data)
        headers = { "Content-Type": "application/json" }
        response = requests.post(post_url, data=d, headers=headers)
        if response.status_code == 200:
            # now link to category
            r = response.json()
            
    def inform_flowdock_spurious(self, accesstoken, client_name, file_path, file_name):
        subject = 'Oops file ' + file_name + ' incorrectly uploaded for ' + client_name
        message = (' \
<div style="float:left;margin: 15 15 15 15"> \
<p>File <b>%s</b> for %s was uploaded to the wrong place</p> \
<p>Files should only be placed in specification folders</p> \
<p>The file was uploaded to: <b>%s</b></p> \
<p>The file has been moved to: <b>/%s/MisplacedFiles</b></p> \
</div>'
            % (file_name, client_name, file_path, client_name))
        post_url = 'https://api.flowdock.com/v1/messages/team_inbox/' + accesstoken
        
        data =  { "source": "PrintFlow 2 Service", "from_address" : "colin@printoutsource.com", \
                    "subject": subject, "content" : message, \
                    "tags": ["@all", "#misplaced_file", file_name] }
        d = json.dumps(data)
        headers = { "Content-Type": "application/json" }
        response = requests.post(post_url, data=d, headers=headers)
        if response.status_code == 200:
            # now link to category
            r = response.json()

    def get_email_spurious_body(self, client_name, file_path, file_name):
        return ('<div>\
<div style="float:left;margin: 15 15 15 15"> \
<p>File <b>%s</b> for %s was uploaded to the wrong place</p> \
<p>Files should only be placed in specification folders</p> \
<p>The file was uploaded to: <b>%s</b></p> \
<p>The file has been moved to: <b>/%s/MisplacedFiles</b></p> \
</div><br style="clear:both" /></div>'
            % (file_name, client_name, file_path, client_name))

    def get_email_file_uploaded_body(self, project, specification, db_file):
        proj = project['noosh_project']
        spec = specification['noosh_specification']
        return (' \
<h3>A file has been uploaded for "%s"</h3> \
<div id="wrap" style="border-top-style:solid;border-top-width:1px;border-top-color:#666666;border-bottom-style:solid;border-bottom-width:1px;border-bottom-color:#666666">\
<div style="float:left;margin: 15 15 15 15"> \
<table> \
<tr><td>Uploaded By:</td><td>%s</td></tr> \
<tr><td>Client:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Reference:</td><td>%s</td></tr> \
<tr><td>Original File Name:</td><td>%s</td></tr> \
<tr><td>Production Name:</td><td>%s</td></tr> \
<tr><td>Size:</td><td>%s bytes</td></tr> \
<tr><td>Upload Time:</td><td>%s</td></tr> \
<tr><td>Pre-flight Status:</td><td>%s</td></tr> \
<tr><td>View pre-flight report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
</table></div> \
<div style="float: left;margin-bottom:15;margin-top:15;border-style:solid;border-width:1px;border-color:#666666"> \
<div style="margin:15 15 15 15"><a href="%s"><img src="%s"></a></div></div><br style="clear:both" /></div>'
            % (spec['spec_name'], db_file['uploaded_by'], proj['client_account'], proj['project_name'], str(proj['project_id']), \
               spec['spec_name'], str(spec['spec_id']), str(spec['reference_number']),\
               db_file['original_name'], db_file['dam_name'], str(db_file['size']), utils.parse_time(db_file['upload_time'], \
               utils.STYLE_DATE_TIME_SHORT_MONTH), db_file['preflight_info'], \
               db_file['preflight_report_html'], \
               db_file['download_url'], db_file['thumbnail_url']))

    def get_email_file_rejected_body(self, proj, spec, db_file):
        return (' \
<h3>A file has been rejected for "%s"</h3> \
<div id="wrap" style="border-top-style:solid;border-top-width:1px;border-top-color:#666666;border-bottom-style:solid;border-bottom-width:1px;border-bottom-color:#666666">\
<div style="float:left;margin: 15 15 15 15"> \
<table> \
<tr><td>Uploaded By:</td><td>%s</td></tr> \
<tr><td>Client:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Reference:</td><td>%s</td></tr> \
<tr><td>Original File Name:</td><td>%s</td></tr> \
<tr><td>Production Name:</td><td>%s</td></tr> \
<tr><td>Size:</td><td>%s bytes</td></tr> \
<tr><td>Upload Time:</td><td>%s</td></tr> \
<tr><td>Pre-flight Status:</td><td>%s</td></tr> \
<tr><td>View HTML Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View Text_Report Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View PDF Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
</table> \
</div> \
<div style="float: left;margin-bottom:15;margin-top:15;border-style:solid;border-width:1px;border-color:#666666"> \
<div style="margin:15 15 15 15"><a href="%s"><img src="%s"></a></div> \
</div><br style="clear:both" /></div>' \
            % (spec['spec_name'], db_file['uploaded_by'], proj['client_account'], proj['project_name'], str(proj['project_id']), \
               spec['spec_name'], str(spec['spec_id']), str(spec['reference_number']),\
               db_file['original_name'], db_file['dam_name'], str(db_file['size']), \
               utils.parse_time(db_file['upload_time'], utils.STYLE_DATE_TIME_SHORT_MONTH), db_file['preflight_info'], \
               db_file['preflight_report_html'], db_file['preflight_report_text'], db_file['preflight_report_mask'], \
               db_file['preflight_report_html'], db_file['thumbnail_url']))

    def build_file_web_page(self, proj, spec, db_file):
        html = ' \
<html><head><title>%s File Information</title></head><body> \
<h3>A file has been uploaded for "%s"</h3> \
<div id="wrap" style="border-top-style:solid;border-top-width:1px;border-top-color:#666666;border-bottom-style:solid;border-bottom-width:1px;border-bottom-color:#666666">\
<div style="float:left;margin: 15 15 15 15"> \
<table> \
<tr><td>Uploaded By:</td><td>%s</td></tr> \
<tr><td>Client:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Reference:</td><td>%s</td></tr> \
<tr><td>Original File Name:</td><td>%s</td></tr> \
<tr><td>Production Name:</td><td>%s</td></tr> \
<tr><td>Size:</td><td>%s bytes</td></tr> \
<tr><td>Upload Time:</td><td>%s</td></tr> \
<tr><td>Pre-flight Status:</td><td>%s</td></tr> \
<tr><td>View HTML Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View Text_Report Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View PDF Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
</table> \
</div> \
<div style="float: left;margin-bottom:15;margin-top:15;border-style:solid;border-width:1px;border-color:#666666"> \
<div style="margin:15 15 15 15"><a href="%s"><img src="%s"></a></div> \
</div><br style="clear:both" /></div>' \
            % (db_file['original_name'], spec['spec_name'], db_file['uploaded_by'], proj['client_account'], proj['project_name'], str(proj['project_id']), \
               spec['spec_name'], str(spec['spec_id']), str(spec['reference_number']),\
               db_file['original_name'], db_file['dam_name'], str(db_file['size']), \
               utils.parse_time(db_file['upload_time'], utils.STYLE_DATE_TIME_SHORT_MONTH), db_file['preflight_info'], \
               db_file['preflight_report_html'], db_file['preflight_report_text'], db_file['preflight_report_mask'], \
               db_file['preflight_report_html'], db_file['thumbnail_url'])

        index_folder = utils.get_guid_path(self.web_rootdir, db_file['guid'])
        index_file = os.path.join(index_folder, 'index.html')
        f = open(index_file, 'w')
        f.write(html)
        f.write(utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address))
        f.write('</body></html>')
        f.close()
            
    def upload_file_to_cumulus(self, client, file_path, file_name, file_pathname, project, spec, status, info, output, guid, \
                             report_file_mask, report_file_text, report_file_html, \
                             uploaded_by):
        self.logger.info("Uploading file:" + file_pathname + " to Cumulus")
        file_object = None
        try:
            url = self.cumulus_api_url + '/file/' + self.workgroup['dam_site'] + '/upload'
            name_bits = file_name.split('.')
            ext = 'pdf'
            if len(name_bits) > 1:
                ext = name_bits[-1]
            file_id = str(project['noosh_project']['project_id']) + "_" + str(spec['noosh_specification']['reference_number'])
            file_object = self.jds.fetch(self.FILE_CLASS, file_id)
            file_exists = False
            if file_object is None:
                file_object = {}
                file_object['versions'] = {}
                file_object['version'] = 1
            else:
                file_exists = True
                old_file_version = {}
                old_file_version['path'] = file_object['path']
                old_file_version['ext'] = file_object['ext']
                old_file_version['size'] = file_object['size']
                old_file_version['version'] = file_object['version']
                old_file_version['guid'] = file_object['guid']
                old_file_version['upload_time'] = file_object['upload_time']
                old_file_version['original_name'] = file_object['original_name']
                old_file_version['dam_name'] = file_object['dam_name']
                old_file_version['dam_id'] = file_object['dam_id']
                old_file_version['dam_site'] = file_object['dam_site']
                old_file_version['download_url'] = file_object['download_url']
                old_file_version['thumbnail_url'] = file_object['thumbnail_url']
                old_file_version['noosh_file_id'] = file_object['noosh_file_id']
                old_file_version['preflight_status'] = file_object['preflight_status']
                old_file_version['preflight_info'] = file_object['preflight_info']
                old_file_version['preflight_output'] = file_object['preflight_output']
                file_object['versions'][str(file_object['version'])] = old_file_version
                file_object['version'] = file_object['version'] + 1
                old_file_version['preflight_report_html'] = file_object['preflight_report_html']
                old_file_version['preflight_report_mask'] = file_object['preflight_report_mask']
                old_file_version['preflight_report_text'] = file_object['preflight_report_text']
                old_file_version['client'] = file_object['client']
                old_file_version['uploaded_by'] = file_object['uploaded_by']
                
            new_file_name = file_id + '_' + str(file_object['version']) + '.' + ext
            new_file_url = utils.get_guid_url(self.web_baseurl, str(guid))    
                
            file_object['id'] = str(project['noosh_project']['project_id']) + "_" + str(spec['noosh_specification']['reference_number'])
            file_object['path'] = file_path
            file_object['ext'] = ext
            file_object['size'] = os.path.getsize(file_pathname)
            file_object['original_name'] = file_name
            file_object['dam_name'] = new_file_name
            file_object['dam_site'] = self.workgroup['dam_site']
            file_object['guid'] = str(guid)
            file_object['project_id'] = project['noosh_project']['project_id']
            file_object['spec_id'] = spec['noosh_specification']['reference_number']
            file_object['upload_time'] = time.strftime('%Y%m%d%H%M%S', time.localtime())        
            file_object['preflight_status'] = status
            file_object['preflight_info'] = info
            file_object['preflight_output'] = output
            file_object['preflight_report_html'] = new_file_url + '/' + report_file_html.split('/')[-1]
            file_object['preflight_report_mask'] = new_file_url + '/' + report_file_mask.split('/')[-1]
            file_object['preflight_report_text'] = new_file_url + '/' + report_file_text.split('/')[-1]
            file_object['client'] = project['noosh_project']['client_account']
            file_object['uploaded_by'] = uploaded_by
   
            db_file_path = None
            files = { 'filename': (new_file_name, open(file_pathname,'rb')) }
            data =  { 'name': new_file_name, 'profile' : 'Standard', \
                     'fulcrum_PF Original Name': file_object['original_name'], \
                     'fulcrum_PF GUID' : file_object['guid'],
                     'fulcrum_PF Status' : status,
                     'fulcrum_PF Client' : file_object['client'],
                     'fulcrum_PF Uploaded By' : uploaded_by }
            #headers = { 'content-type':'multipart/form-data' }

            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                # now link to category
                r = response.json()
                asset_id = r['id']
                file_object['dam_id'] = asset_id
                category_id = spec['cumulus_specification']['dam_category_id']
                requestUrl = self.cumulus_api_url + '/data/' + self.workgroup['dam_site'] + '/addrecordtocategory?recordid=' + str(asset_id) + '&categoryid=' + str(category_id)
                disResponse = requests.get(requestUrl)
                #download_url = self.cumulus_api_url + '/file/' + file_object['dam_site'] + '/get/'+file_object['dam_name']+'?id=' + file_object['dam_id']
                download_url = self.cumulus_baseurl + '/file/' + file_object['dam_site'] + '/get/'+file_object['dam_name']+'?fieldkey=PF GUID&fieldvalue=' + file_object['guid']
                file_object['download_url'] = download_url
                thumbnail_url = self.cumulus_baseurl + '/preview/' + file_object['dam_site'] + '/fetch/'+'?id=' + file_object['dam_id'] + '&name=medium'
                file_object['thumbnail_url'] = thumbnail_url
                #http://dis.printflow2.com/preview/point/fetch?id=83&name=thumbnail
                noosh_file_id = self.post_file_to_noosh(client, self.workgroup['id'], \
                                                        project['noosh_project']['project_id'], spec['noosh_specification']['spec_id'], file_object, uploaded_by)
                if noosh_file_id is not None:
                    file_object['noosh_file_id'] = noosh_file_id
                else:
                    file_object['noosh_file_id'] = 0
                utils.ensureDirectoryExistsForUser(spec['dropbox_path']+"/approved", self.os_userid, self.os_groupid, 0o755)
                if file_exists:
                    db_file_path = self.jds.update(self.FILE_CLASS, file_object)
                else:
                    db_file_path = self.jds.create(self.FILE_CLASS, file_object)
                approved_path = file_path + '/approved'
                utils.ensureDirectoryExistsForUser(approved_path, self.os_userid, self.os_groupid, 0o755)
                utils.safe_file_move(file_pathname, approved_path)
            else:
                print 'Failed to upload file: ', file_pathname +" for project: ", str(project['noosh_project']['project_id']), 'and spec: ', str(spec['noosh_specification']['reference_number'])
        except:
            self.logger.info('Error in upload process!')
            traceback.print_exc()
        finally:
            self.logger.info('Upload process finished, check logs for any errors')
            
        return file_object, db_file_path
    
    def register_failed_file(self, file_path, file_name, file_pathname, project, spec, status, info, output, guid, \
                             report_file_mask, report_file_text, report_file_html, uploaded_by):
        self.logger.info("Registering failed (pre-flight check) file:" + file_pathname)
        file_object = None
        db_file_path = None
        try:
            name_bits = file_name.split('.')
            ext = 'pdf'
            if len(name_bits) > 1:
                ext = name_bits[-1]
            file_id = str(project['noosh_project']['project_id']) + "_" + str(spec['noosh_specification']['reference_number'])
            file_object = self.jds.fetch(self.FILE_CLASS, file_id)
            file_exists = False
            if file_object is None:
                file_object = {}
                file_object['versions'] = {}
                file_object['version'] = 1
            else:
                file_exists = True
                old_file_version = {}
                old_file_version['path'] = file_object['path']
                old_file_version['ext'] = file_object['ext']
                old_file_version['size'] = file_object['size']
                old_file_version['version'] = file_object['version']
                old_file_version['guid'] = file_object['guid']
                old_file_version['upload_time'] = file_object['upload_time']
                old_file_version['original_name'] = file_object['original_name']
                old_file_version['dam_name'] = file_object['dam_name']
                old_file_version['dam_id'] = file_object['dam_id']
                old_file_version['dam_site'] = file_object['dam_site']
                old_file_version['download_url'] = file_object['download_url']
                old_file_version['thumbnail_url'] = file_object['thumbnail_url']
                old_file_version['noosh_file_id'] = file_object['noosh_file_id']
                old_file_version['preflight_status'] = file_object['preflight_status']
                old_file_version['preflight_info'] = file_object['preflight_info']
                old_file_version['preflight_output'] = file_object['preflight_output']
                old_file_version['preflight_report_html'] = file_object['preflight_report_html']
                old_file_version['preflight_report_mask'] = file_object['preflight_report_mask']
                old_file_version['preflight_report_text'] = file_object['preflight_report_text']
                file_object['versions'][str(file_object['version'])] = old_file_version
                file_object['version'] = file_object['version'] + 1
                old_file_version['client'] = file_object['client']
                old_file_version['uploaded_by'] = file_object['uploaded_by']
                
            new_file_name = file_id + '_' + str(file_object['version']) + '_report.' + ext
            new_file_url = utils.get_guid_url(self.web_baseurl, str(guid))    
            file_object['id'] = str(project['noosh_project']['project_id']) + "_" + str(spec['noosh_specification']['reference_number'])
            file_object['path'] = file_path
            file_object['ext'] = ext
            file_object['size'] = os.path.getsize(file_pathname)
            file_object['original_name'] = file_name
            file_object['dam_name'] = new_file_name
            file_object['dam_site'] = self.workgroup['dam_site']
            file_object['guid'] = str(guid)
            file_object['project_id'] = project['noosh_project']['project_id']
            file_object['spec_id'] = spec['noosh_specification']['reference_number']
            file_object['upload_time'] = time.strftime('%Y%m%d%H%M%S', time.localtime())        
            file_object['preflight_status'] = status
            file_object['preflight_info'] = info
            file_object['preflight_output'] = output
            file_object['preflight_report_html'] = new_file_url + '/' + report_file_html.split('/')[-1]
            file_object['preflight_report_mask'] = new_file_url + '/' + report_file_mask.split('/')[-1]
            file_object['preflight_report_text'] = new_file_url + '/' + report_file_text.split('/')[-1]
            file_object['client'] = project['noosh_project']['client_account']
            file_object['uploaded_by'] = uploaded_by
    
            asset_id = file_object['guid']
            file_object['dam_id'] = asset_id
            failed_path = file_path + '/failed'
            utils.ensureDirectoryExistsForUser(failed_path, self.os_userid, self.os_groupid, 0o755)
            preview_path = utils.get_guid_path(self.web_rootdir, file_object['guid'])
            utils.ensureDirectoryExistsForUser(preview_path, self.os_userid, self.os_groupid, 0o755)
            preview_file, preview_file_name = self.pdf_preview(file_path, file_name, file_pathname, preview_path)
            #download_url = self.cumulus_baseurl + '/file/' + file_object['dam_site'] + '/get/'+file_object['dam_name']+'?fieldkey=PF GUID&fieldvalue=' + file_object['guid']
            file_object['download_url'] = ''
            thumbnail_url = self.web_baseurl + '/' + file_object['guid'].replace('-', '/') + '/' + preview_file_name
            file_object['thumbnail_url'] = thumbnail_url
            #http://dis.printflow2.com/preview/point/fetch?id=83&name=thumbnail
            file_object['noosh_file_id'] = 0
            utils.ensureDirectoryExistsForUser(spec['dropbox_path']+"/failed", self.os_userid, self.os_groupid, 0o755)
            if file_exists:
                db_file_path = self.jds.update(self.FILE_CLASS, file_object)
            else:
                db_file_path = self.jds.create(self.FILE_CLASS, file_object)
            utils.safe_file_move(file_pathname, failed_path)
        except:
            self.logger.info('Error in file registration process!')
            traceback.print_exc()
        finally:
            self.logger.info('Upload process finished, check logs for any errors')
            
        return file_object, db_file_path

    def pdf_preview(self, file_path, file_name, file_pathname, destination):
        result = None
        try:
            self.logger.info("Creating preview for file:" + file_pathname)
            status, output, preview_file, preview_file_name = self.pdf_toolbox.run_preview(self.workgroup['serial_number'], \
                                                                        file_path, \
                                                                        file_name, \
                                                                        destination)
            result = preview_file, preview_file_name
        except:
            self.logger.info('Error in preview process!')
            traceback.print_exc()
            
        return result
                        
    def preflight_check(self, file_path, file_name, file_pathname, project, spec, guid):
        ok = False
        info = ''
        try:
            self.logger.info("Preflight checking file:" + file_pathname)
            status, output, report_folder, report_file_mask, report_file_text, report_file_html = self.pdf_toolbox.run_job(self.workgroup['serial_number'], file_path, \
                                                                                                                           file_name, self.workgroup['preflight_profile'], os.path.join(file_path, 'approved'), \
                                                                                                                           os.path.join(file_path, 'failed'), guid)
            if status == 0:
                ok = True;
                info = 'Good - No problems'
            elif status == 1:
                ok = True
                info = 'Good - Some possible issues'
            elif status == 2:
                ok = False
                info = 'Good - Some warnings'
            elif status == 3:
                ok = False
                info = 'Fail - Not compliant'
            elif status == 5:
                ok = True
                info = 'Good - No problems, file corrected'
            elif status == 103:
                ok = True
                info = 'Fail - Error processing file'
            elif status == 104:
                ok = True
                info = 'Fail - Cannot open file'
            else:
                ok = False
                
        except:
            self.logger.info('Error in pre-flight process!')
            traceback.print_exc()
            
        return ok, info, output, report_folder, report_file_mask, report_file_text, report_file_html
           
    def post_file_to_noosh(self, client, workgroup_id, project_id, spec_id, file_object, uploaded_by):
        result = None
        url = self.noosh_api + '/workgroups/' + str(workgroup_id) + '/projects/' + str(project_id) + '/files'
        url += '?access_token=' + self.access_token
        data = {}
        data['file_name'] = file_object['dam_name']
        data['file_size'] = file_object['size']
        data['file_type'] = file_object['ext']
        data['file_location'] = file_object['download_url']
        data['is_remote'] = True
        data['description'] = 'Approved print ready file for specification: ' + str(spec_id)
        noosh_post_data = json.dumps(data)
        headers = { 'content-type':'application/json' }
        if 'noosh_nge_enabled' in client and client['noosh_nge_enabled'] is True:
            nooshResponse = requests.post(url, data=noosh_post_data, headers=headers)
            if nooshResponse.status_code == 200:
                # now link to category
                r = nooshResponse.json()
                if r['status_code'] == 200:
                    result = r['result']['file_id']
                else:
                    self.logger.info('Noosh returned error for file upload: ' + str(r['status_code']) + ' with reason: ' + r['status_reason'])
            else:
                self.logger.info('Problem sending file link to Noosh, return code is: ' + nooshResponse.status_code)
        else:
            file_name = file_object['dam_name']
            try:
                user = self.find_upload_user(client['users'], uploaded_by)
                config_upload_by = user['noosh_username']
            except:
                config_upload_by = None
            if config_upload_by is None:
                config_upload_by = self.noosh_soap_api['file_upload_identity']
                if 'account_managers' in client and len(client['account_managers']) > 0:
                    am_id = client['account_managers'][0]
                    if am_id in client['users']:
                        account_manager = client['users'][am_id]
                        if 'noosh_username' in account_manager:
                            config_upload_by = account_manager['noosh_username']
                            if uploaded_by is not None:
                                # using account manager to upload, so add uploader name to the file title sent
                                file_name = file_object['dam_name'] + ' uploaded by ' + uploaded_by
            noosh_soap_body = nooshsoap.createRemoteFileUploadBody(self.noosh_soap_api, config_upload_by, project_id, file_name, file_object['download_url'])
            noosh_soap_message = nooshsoap.createNooshSOAPMessage(self.noosh_soap_api, noosh_soap_body)
            #print noosh_soap_message
            headers = { 'Content-Type':'text/xml; charset=UTF-8' }
            nooshResponse = requests.post(self.noosh_soap_api['url'], data=noosh_soap_message, headers=headers)
            if nooshResponse.status_code == 200:
                r = nooshResponse
        return result
    
    def find_upload_user(self, users, uploaded_by):
        result = None
        for user_id in users:
            user = users[user_id]
            if 'dropbox_folder' in user and user['dropbox_folder'] == uploaded_by:
                result = user
                break
        return result
