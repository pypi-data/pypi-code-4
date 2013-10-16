'''
Created on Sep 19, 2013

@author: "Colin Manning"
'''
import requests
import time
import datetime
import os
import json
import logging
import smtplib
import traceback
from email.mime.text import MIMEText
from JDs import JDs
import utils
import pyinotify

COMMASPACE = ', '    

class NooshMonitor(pyinotify.ProcessEvent):
    '''
    Monitor Noosh for project and specifications
    '''
    config_data = None
    
    WORKGROUP_CLASS = 'workgroup'
    PROJECT_CLASS = 'project'
    SPECIFICATION_CLASS = 'specification'
    FILE_CLASS = 'file'
    USER_CLASS = 'user'
    nooshApiUrl = "http://demo.scd.noosh.com/api/v1"
    cumulusApiUrl = "http://dis.printflow2.com"
    cumulusBaseUrl = "http://localhost:8080/disweb"
    accessToken = ""
    pdfoolboxPath = "/opt/priontflow2/callas/bin/pdfToolboxServer.bin"
    check_interval = 10
    dbDir = ''
    jds = None
    workgroupId = None
    theWorkgroup = {}
    ready = False
    logger = None
    mail_server = None
    mailer = None
    mail_signature_logo = None
    company_web_address = None
    wm = None
    notifier = None
    wdd = None
    os_userid = None
    os_groupid = None
    fileSystemMonitor = None
    
    CREATE_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CREATE']
    MODIFY_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_MODIFY']
    watch_mask = CREATE_EVENT | MODIFY_EVENT
   
    def __init__(self,config_file, workgroup_id, fileSystemMonitor):
        self.config_data = config_file
        if os.path.exists(config_file):
            with open(config_file) as f:
                self.config_data = json.load(f)
                f.close()
        if self.config_data is not None:
            self.logger = logging.getLogger('printflow2')

            self.nooshApiUrl = self.config_data['nooshapi']
            self.cumulusApiUrl = self.config_data['cumulusapi']
            self.cumulusBaseUrl = self.config_data['cumulusbaseurl']
            self.accessToken = self.config_data['accesstoken']
            self.pdfoolboxPath = self.config_data['pdftoolbox']
            self.check_interval = self.config_data['checkinterval']
            self.dbDir = self.config_data['dbdir']
            self.logger.info("Database directory: " + self.dbDir)
            self.logger.info("Noosh API: " + self.nooshApiUrl)
            self.logger.info("Cumulus API: " + self.cumulusApiUrl)
            self.logger.info("Cumulus Base URL: " + self.cumulusBaseUrl)
            self.logger.info("PDF Toolbox: " + self.pdfoolboxPath)
            self.logger.info("Noosh check interval: " + str(self.check_interval))
            self.mail_server = self.config_data['mail_server']
            self.setup_mailer(self.mail_server)
            self.company_web_address = self.config_data['company_web_address']
            self.os_userid = self.config_data['os_userid']
            self.os_groupid = self.config_data['os_groupid']
            
            self.jds = JDs(self.dbDir, self.os_userid, self.os_groupid)
            self.jds.register_class(self.WORKGROUP_CLASS)
            self.jds.register_class(self.PROJECT_CLASS)
            self.jds.register_class(self.SPECIFICATION_CLASS)
            self.jds.register_class(self.FILE_CLASS)
            self.jds.register_class(self.USER_CLASS)
            self.workgroupId = workgroup_id
            self.theWorkgroup = self.jds.fetch(self.WORKGROUP_CLASS, self.workgroupId)
            self.fileSystemMonitor = fileSystemMonitor
            
            if 'killfile' in self.config_data:
                pyinotify.ProcessEvent.__init__(self)
                self.wm = pyinotify.WatchManager()
                self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
                self.wdd = self.wm.add_watch(os.path.dirname(self.config_data['killfile']), self.watch_mask, rec=False, auto_add=True)
                self.ready = True
        else:
            self.ready = False
            print 'Failed to load config file: ', config_file
            
    def process_IN_CREATE(self, event):
        if event.pathname == self.config_data['killfile']:
            self.stop()
        
    def process_IN_MODIFY(self, event):
        if event.pathname == self.config_data['killfile']:
            self.stop()

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
            
    def start(self):
        while self.ready:
            try:
                ok = True
                this_check_time = time.strftime('%Y%m%d%H%M%S', time.localtime())        
        
                self.logger.info("Checking Noosh for project activity in workgroup: '" + self.theWorkgroup['name'] + "' with id: '"+ str(self.theWorkgroup['id']) + "' at " + str(this_check_time))
                last_check_time = time.strptime(self.theWorkgroup['last_check'], '%Y%m%d%H%M%S')
                ok = self.checkForProjects(self.theWorkgroup, last_check_time, 'create_date_from', True) # check for creates
                if ok: 
                    ok = self.checkForProjects(self.theWorkgroup, last_check_time, 'mod_date_from', False) # check for modifies
                if ok:
                    ok = self.checkForProjects(self.theWorkgroup, last_check_time, 'last_spec_update_from', False) # check for spec updates
    
                # save check time after all done
                if ok:
                    self.theWorkgroup['last_check'] = this_check_time
                    self.jds.update(self.WORKGROUP_CLASS, self.theWorkgroup)
                    self.fileSystemMonitor.scanFolders()
            except:
                self.logger.error('Problem communicating with Noosh - will try again in '+self.check_interval+' seconds.')
            finally:
                time.sleep(self.check_interval)
                
    def stop(self):
        self.ready = False
 
    '''
     The worker methods
    '''
    def createDamProjectCategory(self, workgroup, project):
        # http://dis.printflow2.com/data/vodacom/create?item=category&path=$Categories:Demo:Colin
        project_path = project['client_account'] +":Projects:" + str(project['project_id']) + ' - ' + project['project_name']
        category_path = '$Categories:' + project_path
        requestUrl = self.cumulusApiUrl +"/data/" + workgroup['dam_site'] + '/create?item=category&path=' + category_path
        disResponse = requests.get(requestUrl)
        response = disResponse.json()
        result = {}
        result['class'] = self.PROJECT_CLASS
        result['id'] = project['project_id']
        result['id_parent'] = project['workgroup_id']
        result['class_parent'] = self.WORKGROUP_CLASS
        result['noosh_project'] = project
        
        cumulus_project = {}
        cumulus_project['dam_category_path'] = category_path
        cumulus_project['dam_category_id'] = response['id']
        cumulus_project['dam_site'] = workgroup['dam_site']
        result['cumulus_project'] = cumulus_project
        
        result['dropbox_path'] = workgroup['dropbox_root'] + '/' + project['client_account'] +"/Projects/" + str(project['project_id'])
        utils.ensureDirectoryExistsForUser(result['dropbox_path'], self.os_userid, self.os_groupid, 0o755)
        return result

    def createDamSpecificationCategory(self, project, spec):
        category_path = project['cumulus_project']['dam_category_path'] + ":" + spec['reference_number']
        requestUrl = self.cumulusApiUrl +"/data/" + project['cumulus_project']['dam_site'] + '/create?item=category&path=' + category_path
        disResponse = requests.get(requestUrl)
        result = {}
        response = disResponse.json()
        result['class'] = self.SPECIFICATION_CLASS
        result['id'] = spec['reference_number']
        result['id_parent'] = project['id']
        result['class_parent'] = self.PROJECT_CLASS
        result['noosh_specification'] = spec
        
        cumulus_specification = {}
        cumulus_specification['dam_category_path'] = category_path
        cumulus_specification['dam_category_id'] = response['id']
        cumulus_specification['dam_site'] = project['cumulus_project']['dam_site']
        result['cumulus_specification'] = cumulus_specification
    
        result['dropbox_path'] = project['dropbox_path'] + "/" + str(spec['reference_number'])
        utils.ensureDirectoryExistsForUser(result['dropbox_path'], self.os_userid, self.os_groupid, 0o755)
        # create a file that shows the spec name for convenience
        name_file = os.path.join(result['dropbox_path'], result['noosh_specification']['spec_name']) + '.json'
        with open(name_file, "w") as f:
            f.write(json.dumps(result, indent=3))
        return result

    def checkForProjectSpecifications(self, workgroup, project):
        offset = 0
        count = 1000
        filters = '{"limit":1000, "offset":0}'
        #filters = urllib.quote_plus(filters)
        requestUrl = self.nooshApiUrl + "/workgroups/" + str(workgroup['id']) + "/projects/" + str(project['id']) + "/specs?access_token=" + self.accessToken + "&filters=" + filters
        nooshResponse = requests.get(requestUrl)
        response = nooshResponse.json()
        specs = None
        while response['status_code'] == 200:
            specs = response['results']
            for i in range(len(specs)):
                self.processSpecification(project, specs[i])
            offset += count
            filters = '{"limit":'+str(count)+', "offset":' + str(offset)+'}'
            #filters = urllib.quote_plus(filters)
            requestUrl = self.nooshApiUrl + "/workgroups/" + str(workgroup['id']) + "/projects/" + str(project['id']) + "/specs?access_token=" + self.accessToken + "&filters=" + filters
            nooshResponse = requests.get(requestUrl)
            response = nooshResponse.json()
        return specs

    def getNooshProjectDetails(self, workgroup, project):
        requestUrl = self.nooshApiUrl + "/workgroups/" + str(workgroup['id']) + "/projects/" + str(project['project_id']) +"?access_token=" + self.accessToken
        nooshResponse = requests.get(requestUrl)
        result = nooshResponse.json()
        if result['status_code'] == 200:
            return result['result']            
    
    def addNewClient(self, client_name):
        result = {}
        result['name'] = client_name
        result['id'] = ""
        result['dam_site'] = self.theWorkgroup['dam_site']
        self.theWorkgroup['clients'][client_name] = result
        return result

    def processProject(self, workgroup_last_check, workgroup, project, project_filter, send_email):
        print 'Processing project: ', str(project['project_id']), project['project_name'] +" for '" + project_filter +"'"
        proj = self.jds.fetch(self.PROJECT_CLASS, project['project_id'])
        proj_is_new = (proj is None)
            
        project_details = self.getNooshProjectDetails(workgroup, project)
        project_details['workgroup_id'] = workgroup['id']
        if project['client_account'] is not None:
            # we need a client account, if not existing, then we need to pick it up in modification
            if project['client_account'] in workgroup['clients']:
                client = workgroup['clients'][project['client_account']]
            else:
                client = self.addNewClient(project['client_account'])
            if project_details['project_description'] is None:
                project_details['project_description'] = ''
            if project_details['comments'] is None:
                project_details['comments'] = ''
            db_project = self.createDamProjectCategory(workgroup, project_details)
            self.jds.create(self.PROJECT_CLASS, db_project)
            specs = self.checkForProjectSpecifications(workgroup, db_project)
            proj = db_project['noosh_project']
            if proj_is_new and send_email:
                subject = 'Project Created for ' + project['client_account']
                message = self.get_email_project_create_body(proj)            
                for i in range(len(specs)):
                    spec = specs[i]
                    message += self.get_email_specification_body(proj, spec)
                message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)
                self.send_html_mail(client['project_notify_emails'], subject, message)    
                if workgroup['clients'][project['client_account']]['flowdock_accesstoken'] is not None:
                    self.inform_flowdock(workgroup['clients'][project['client_account']]['flowdock_accesstoken'], proj, specs)
                    
                
        else:
            print ' - aborting project', str(project['project_id']), ', no client account available'
            
    def inform_flowdock(self, accesstoken, proj, specs):
        
        subject = 'Project ' + proj['project_name'] + ' created'
        #message = 'A new project '+proj['project_name']+' has been created with id: "'+str(proj['project_id']) + '. \
#with the following specifications:'

        message = ('<div>\
<h3>A new project has been created:</h3> \
<table> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Description:</td><td>%s</td></tr>\
<tr><td>Comments:</td><td>%s</td></tr> \
</table></div><br /><div>Specifications:</div><hr />'
        % (proj['project_id'], proj['project_name'], proj['project_description'], proj['comments']))

        for i in range(len(specs)):
            spec = specs[i]
            message += self.get_email_specification_body(proj, spec)

        post_url = 'https://api.flowdock.com/v1/messages/team_inbox/' + accesstoken
        
        data =  { "source": "PrintFlow 2 Service", "from_address" : "colin@printoutsource.com", \
                    "subject": subject, "content" : message, \
                    "project": str(proj['project_id']), \
                    "tags": ["@all", "#project", str(proj['project_id'])] }
        d = json.dumps(data)
        headers = { "Content-Type": "application/json" }
        response = requests.post(post_url, data=d, headers=headers)
        if response.status_code == 200:
            # now link to category
            r = response.json()
        
        
    def get_email_project_create_body(self, proj):
        return ('<div>\
<h3>A new project has been created:</h3> \
<table> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Description:</td><td>%s</td></tr>\
<tr><td>Comments:</td><td>%s</td></tr> \
</table></div><br /><div>Specifications:</div><hr />'
        % (proj['project_id'], proj['project_name'], proj['project_description'], proj['comments']))

    def get_email_specification_body(self, proj, spec):
        return ('<div> \
<table> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Reference No:</td><td> %s</td></tr> \
</table> \
<hr /></div>'
        % (spec['spec_id'], spec['spec_name'], spec['reference_number']))

    def processSpecification(self, project, spec):
        print 'Processing specification: ', str(spec['spec_id']), spec['spec_name']
        db_spec = self.createDamSpecificationCategory(project, spec)
        self.jds.create(self.SPECIFICATION_CLASS, db_spec)
    
    def checkForProjects(self, workgroup, last_check_time, project_filter, send_email):
        ok = False
        try:
            workgroup_id = str(workgroup['id'])
            #workgroup_last_check = datetime.datetime.fromtimestamp(workgroup['last_check']).isoformat()
            workgroup_last_check = datetime.datetime.fromtimestamp(time.mktime(last_check_time)).isoformat()
            localtime = time.localtime()
            timezone = -(time.altzone if localtime.tm_isdst else time.timezone)
            check_time = workgroup_last_check
            # %2B is +, %2D is -
            check_time += ".000Z" if timezone == 0 else ".000%2B" if timezone > 0 else ".000%2D"
            check_time += time.strftime("%H:%M", time.gmtime(abs(timezone)))
        
            count = 10
            offset = 0
            filters = '{"limit":'+str(count) + ', "offset":' + str(offset) + ',"'+project_filter+'":"' + check_time + '"}'
            #filters = urllib.quote_plus(filters)
            
            requestUrl = self.nooshApiUrl + "/workgroups/" + workgroup_id + "/projects?access_token=" + self.accessToken + "&filters=" + filters
            nooshResponse = requests.get(requestUrl)
            r = nooshResponse.json()
            while r['status_code'] == 200:
                projects = r['results']
                for i in range(len(projects)):
                    self.processProject(workgroup_last_check, workgroup, projects[i], project_filter, send_email)
                offset += count
                filters = '{"limit":'+str(count) + ', "offset":' + str(offset) + ',"'+project_filter+'":"' + check_time + '"}'
                #filters = urllib.quote_plus(filters)
                
                requestUrl = self.nooshApiUrl + "/workgroups/" + workgroup_id + "/projects?access_token=" + self.accessToken + "&filters=" + filters
                nooshResponse = requests.get(requestUrl)
                r = nooshResponse.json()
            ok = True
        except:
            self.logger.error('Problem getting projects data from Noosh')
            traceback.print_exc()
            ok = False
        return ok
