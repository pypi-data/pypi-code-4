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

from JDs import JDs
from PdfToolbox import PdfToolbox
import utils

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
    
    ignore_files = ['New folder', '.DS_Store', 'untitled folder', 'approved', 'failed']
    
    created_files = {}
    modified_files = {}
    wdd = None
    wm = None
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
    
    config_data = None
    web_rootdir = None
    web_baseurl = None
    
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
            self.cumulus_api_url = self.config_data['cumulusapi']
            self.cumulus_baseurl = self.config_data['cumuluslbaseurl']
            self.access_token = self.config_data['accesstoken']
            self.pdftoolbox_path = self.config_data['pdftoolbox']
            self.db_dir = self.config_data['dbdir']
            self.web_rootdir = self.config_data['web_server']['rootdir']
            self.web_baseurl = self.config_data['web_server']['baseurl']
            self.os_userid = self.config_data['os_userid']
            self.os_groupid = self.config_data['os_groupid']
            
            self.jds = JDs(self.db_dir, self.os_userid, self.os_groupid)
            self.jds.register_class(self.WORKGROUP_CLASS)
            self.jds.register_class(self.PROJECT_CLASS)
            self.jds.register_class(self.SPECIFICATION_CLASS)
            self.jds.register_class(self.FILE_CLASS)
            self.jds.register_class(self.USER_CLASS)
            self.workgroupId = workgroup_id
            self.workgroup = self.jds.fetch(self.WORKGROUP_CLASS, self.workgroupId)
            self.watch_dir = self.workgroup['dropbox_root']
            
            self.wm = pyinotify.WatchManager()
            self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
            self.wdd = self.wm.add_watch(self.watch_dir, self.watch_mask, rec=True, auto_add=True)
            
            self.mail_server = self.config_data['mail_server']
            self.setup_mailer(self.mail_server)
            self.company_web_address = self.config_data['company_web_address']
            
            self.pdf_toolbox = PdfToolbox(self.config_data['pdftoolbox'], \
                                          self.config_data['pdftoolbox_cache_path'], 
                                          self.config_data['activationcode'], \
                                          self.config_data['pdftoolbox_tmpdir'], \
                                          self.web_rootdir)
            self.ready = True
        else:
            self.ready = False
            print "Failed to load config file: ", config_file

    def start(self):
        self.logger.info("Watching" + str(self.watch_dir))
        self.notifier.start()
        
    def stop(self):
        if (self.wdd is not None) and (self.wdd[self.watch_dir] > 0):
                self.wm.rm_watch(self.wdd[self.watch_dir])
                
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
            send_message = MIMEText(message, 'html')
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
            self.logger.error('problem sending html email')            
            traceback.print_exc()
            
            
    def is_ready(self):
        return self.ready
            
    def process_IN_CREATE(self, event):
        if self._ignore_file(event.name):
            return
        
        #print "Create Event:", event
        pathname = os.path.join(event.path, event.name)
        self.created_files[pathname] = event.maskname
        
    def process_IN_MODIFY(self, event):
        if self._ignore_file(event.name):
            return
        
        self.logger.info("Modify Event:" + str(event))
        pathname = os.path.join(event.path, event.name)
        self.modified_files[pathname] = event.maskname
    
    # we get this when a file is changed and closed in the folder directly
    def process_IN_CLOSE_WRITE(self, event):
        if self._ignore_file(event.name):
            return
        
        self.logger.info("Close Write:" + str(event))
        pathname = os.path.join(event.path, event.name)

    # we seem to get this when file deleted form network folder (e.g. Dropbox)
    def process_IN_MOVED_FROM(self, event):
        if self._ignore_file(event.name):
            return
        #print "Moved From Write:", event
        pathname = os.path.join(event.path, event.name)
        if os.path.exists(pathname):
            st = os.stat(pathname)

    # file created over network (e.g. Dropbox)
    def process_IN_MOVED_TO(self, event):
        if self._ignore_file(event.name):
            return
        path_bits = event.path.split('/')
        if path_bits[-1] == 'approved':
            return
        if path_bits[-1] == 'failed':
            return
        
        try:
            guid = str(uuid.uuid4())
            path_bits = event.path.split('/')
            project = self.jds.fetch(self.PROJECT_CLASS, path_bits[-2])
            specification = self.jds.fetch(self.SPECIFICATION_CLASS, path_bits[-1])
            workgroup = self.jds.fetch(self.WORKGROUP_CLASS, project['id_parent'])
            client = workgroup['clients'][project['noosh_project']['client_account']]
            status, info, output, report_folder, report_file_mask, report_file_text, report_file_html = self.preflight_check(event, project, specification, guid)
            db_file_path = None
            db_file = None
            proj = None
            spec = None
            if status:
                approved_path = os.path.join(event.path, "approved")
                utils.ensureDirectoryExistsForUser(approved_path, self.os_userid, self.os_groupid, 0o755)
                db_file, db_file_path = self.upload_file_to_cumulus(event, project, specification, status, info, output, guid, \
                                                                  report_file_mask, report_file_text, report_file_html)
                proj = project['noosh_project']
                spec = specification['noosh_specification']
                subject = 'File uploaded for ' + proj['client_account'] + ' - Project ' +proj['project_name'] + ' (' + str(proj['project_id'])+')'
                message = self.get_email_file_uploaded_body(proj, spec, db_file)
                message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)            
                self.send_html_mail(client['file_notify_emails'], subject, message)
                if workgroup['clients'][proj['client_account']]['flowdock_accesstoken'] is not None:
                    self.inform_flowdock_uploaded(workgroup['clients'][proj['client_account']]['flowdock_accesstoken'], proj, spec, db_file)
            else:
                proj = project['noosh_project']
                spec = specification['noosh_specification']
                db_file, db_file_path = self.register_failed_file(event, project, specification, status, info, output, guid, \
                                                                  report_file_mask, report_file_text, report_file_html)
                subject = 'File rejected for ' + proj['client_account'] + ' - Project ' +proj['project_name'] + ' (' + str(proj['project_id'])+')'
                message = self.get_email_file_rejected_body(proj, spec, db_file)
                message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)            
                self.send_html_mail(client['file_notify_emails'], subject, message)
                self.logger.info('pre-flight check failed file: ' + event.pathname)
                if workgroup['clients'][proj['client_account']]['flowdock_accesstoken'] is not None:
                    self.inform_flowdock_rejected(workgroup['clients'][proj['client_account']]['flowdock_accesstoken'], proj, spec, db_file)
            self.build_file_web_page(proj, spec, db_file)        

        except:
            self.logger.error('Problem processing file')
            traceback.print_exc()

    # we seem to get this on directory delete, but not file delete, if file is network (e.g. Dropbox)
    def process_IN_DELETE(self, event):
        if self._ignore_file(event.name):
            return
        
        self.logger.info("Delete Write:" + str(event))
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
                    "tags": ["@all", "#project", str(proj['project_id']), str(spec['spec_id'])] }
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

    def get_email_file_uploaded_body(self, proj, spec, db_file):
        return (' \
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

    def get_email_file_rejected_body(self, proj, spec, db_file):
        return (' \
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

    def build_file_web_page(self, proj, spec, db_file):
        html = ' \
<html><head><title>%s File Information</title></head><body> \
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
<tr><td>View HTML Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View Text_Report Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
<tr><td>View PDF Report:</td><td><a href="%s" target="_blank">here</a></td></tr> \
</table> \
</div> \
<div style="float: left;margin-bottom:15;margin-top:15;border-style:solid;border-width:1px;border-color:#666666"> \
<div style="margin:15 15 15 15"><a href="%s"><img src="%s"></a></div> \
</div><br style="clear:both" /></div>' \
            % (db_file['original_name'], spec['spec_name'], proj['client_account'], proj['project_name'], str(proj['project_id']), \
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
            
    def upload_file_to_cumulus(self, file_event, project, spec, status, info, output, guid, \
                             report_file_mask, report_file_text, report_file_html):
        self.logger.info("Uploading file:" + file_event.pathname + " to Cumulus")
        file_object = None
        try:
            url = self.cumulus_api_url + '/file/' + self.workgroup['dam_site'] + '/upload'
            name_bits = file_event.name.split('.')
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
                
            new_file_name = file_id + '_' + str(file_object['version']) + '.' + ext
            new_file_url = utils.get_guid_url(self.web_baseurl, str(guid))    
                
            file_object['id'] = str(project['noosh_project']['project_id']) + "_" + str(spec['noosh_specification']['reference_number'])
            file_object['path'] = file_event.path
            file_object['ext'] = ext
            file_object['size'] = os.path.getsize(file_event.pathname)
            file_object['original_name'] = file_event.name
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
    
            db_file_path = None
            files = { 'filename': (new_file_name, open(file_event.pathname,'rb')) }
            data =  { 'name': new_file_name, 'profile' : 'Standard', 'fulcrum_PF Original Name': file_object['original_name'], 'fulcrum_PF GUID' : file_object['guid'] }
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
                noosh_file_id = self.post_file_to_noosh(self.workgroup['id'], project['noosh_project']['project_id'], spec['noosh_specification']['spec_id'], file_object)
                if noosh_file_id is not None:
                    file_object['noosh_file_id'] = noosh_file_id
                else:
                    file_object['noosh_file_id'] = 0
                utils.ensureDirectoryExistsForUser(spec['dropbox_path']+"/approved", self.os_userid, self.os_groupid, 0o755)
                if file_exists:
                    db_file_path = self.jds.update(self.FILE_CLASS, file_object)
                else:
                    db_file_path = self.jds.create(self.FILE_CLASS, file_object)
                approved_path = file_event.path + '/approved'
                utils.ensureDirectoryExistsForUser(approved_path, self.os_userid, self.os_groupid, 0o755)
                utils.safe_file_move(file_event.pathname, approved_path)
            else:
                print 'Failed to upload file: ', file_event.pathname +" for project: ", str(project['noosh_project']['project_id']), 'and spec: ', str(spec['noosh_specification']['reference_number'])
        except:
            self.logger.info('Error in upload process!')
            traceback.print_exc()
        finally:
            self.logger.info('Upload process finished, check logs for any errors')
            
        return file_object, db_file_path
    
    def register_failed_file(self, file_event, project, spec, status, info, output, guid, \
                             report_file_mask, report_file_text, report_file_html):
        self.logger.info("Registering failed (pre-flight check) file:" + file_event.pathname)
        file_object = None
        db_file_path = None
        try:
            name_bits = file_event.name.split('.')
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
                
            new_file_name = file_id + '_' + str(file_object['version']) + '_report.' + ext
            new_file_url = utils.get_guid_url(self.web_baseurl, str(guid))    
            file_object['id'] = str(project['noosh_project']['project_id']) + "_" + str(spec['noosh_specification']['reference_number'])
            file_object['path'] = file_event.path
            file_object['ext'] = ext
            file_object['size'] = os.path.getsize(file_event.pathname)
            file_object['original_name'] = file_event.name
            file_object['dam_name'] = new_file_name
            file_object['dam_site'] = self.web_baseurl
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
    
            asset_id = file_object['guid']
            file_object['dam_id'] = asset_id
            failed_path = file_event.path + '/failed'
            utils.ensureDirectoryExistsForUser(failed_path, self.os_userid, self.os_groupid, 0o755)
            preview_path = utils.get_guid_path(self.web_rootdir, file_object['guid'])
            utils.ensureDirectoryExistsForUser(preview_path, self.os_userid, self.os_groupid, 0o755)
            preview_file, preview_file_name = self.pdf_preview(file_event, preview_path)
            download_url = self.cumulus_baseurl + '/file/' + file_object['dam_site'] + '/get/'+file_object['dam_name']+'?fieldkey=PF GUID&fieldvalue=' + file_object['guid']
            file_object['download_url'] = download_url
            thumbnail_url = self.web_baseurl + '/' + file_object['guid'].replace('-', '/') + '/' + preview_file_name
            file_object['thumbnail_url'] = thumbnail_url
            #http://dis.printflow2.com/preview/point/fetch?id=83&name=thumbnail
            file_object['noosh_file_id'] = 0
            utils.ensureDirectoryExistsForUser(spec['dropbox_path']+"/failed", self.os_userid, self.os_groupid, 0o755)
            if file_exists:
                db_file_path = self.jds.update(self.FILE_CLASS, file_object)
            else:
                db_file_path = self.jds.create(self.FILE_CLASS, file_object)
            utils.safe_file_move(file_event.pathname, failed_path)
        except:
            self.logger.info('Error in file registration process!')
            traceback.print_exc()
        finally:
            self.logger.info('Upload process finished, check logs for any errors')
            
        return file_object, db_file_path

    def pdf_preview(self, file_event, destination):
        result = None
        try:
            self.logger.info("Creating preview for file:" + file_event.pathname)
            status, output, preview_file, preview_file_name = self.pdf_toolbox.run_preview(self.workgroup['serial_number'], \
                                                                        file_event.path, \
                                                                        file_event.name, \
                                                                        destination)
            result = preview_file, preview_file_name
        except:
            self.logger.info('Error in preview process!')
            traceback.print_exc()
            
        return result
                        
    def preflight_check(self, file_event, project, spec, guid):
        ok = False
        info = ''
        try:
            self.logger.info("Preflight checking file:" + file_event.pathname)
            status, output, report_folder, report_file_mask, report_file_text, report_file_html = self.pdf_toolbox.run_job(self.workgroup['serial_number'], file_event.path, file_event.name, self.workgroup['preflight_profile'], os.path.join(file_event.path, 'approved'), os.path.join(file_event.path, 'failed'), guid)
            if status == 0:
                ok = True;
                info = 'Good - No problems'
            elif status == 1:
                ok = False
                info = 'Fail - Some problems'
            elif status == 2:
                ok = True
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
           
    def post_file_to_noosh(self, workgroup_id, project_id, spec_id, file_object):
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
        return result
