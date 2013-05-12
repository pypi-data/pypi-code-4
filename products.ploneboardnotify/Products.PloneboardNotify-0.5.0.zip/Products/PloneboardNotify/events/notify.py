# -*- coding: utf-8 -*-

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from Products.PloneboardNotify.interfaces import ILocalBoardNotify
from Products.PloneboardNotify import html_template

try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
except ImportError: # py24
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText

import re

raw_url_finder = r"""<a.*?class=\"internal-link\".*?href=\"(?P<url1>.*?)\".*?</a>"""
"""|<a.*?href=\"(?P<url2>.*?)\".*?class=\"internal-link\".*?</a>"""
url_finder = re.compile(raw_url_finder)

match_start = "href=\""

def _getAllValidEmailsFromGroup(putils, acl_users, group):
    """Look at every user in the group, return all valid emails"""
    return [m.getProperty('email') for m in group.getGroupMembers() if putils.validateSingleEmailAddress(m.getProperty('email'))]

def _getConfiguration(object):
    """Return the local or global configuration settings for notify"""
    # BBB: the best is to refactor this using adapters
    if not ILocalBoardNotify.providedBy(object):
        ploneboard_notify_properties = getToolByName(object,'portal_properties')['ploneboard_notify_properties']
        sendto_all = ploneboard_notify_properties.sendto_all
        sendto_values = ploneboard_notify_properties.sendto_values
    else:
        # Local configuration
        sendto_all = object.getProperty('forum_sendto_all', False)
        sendto_values = object.getProperty('forum_sendto_values', [])
    return sendto_all, sendto_values


def _getSendToValues(object):
    """Load the portal configuration for the notify system and obtain a list of emails.
    If the sendto_all is True, the mail will be sent to all members of the Plone site.
    The sendto_values value is used to look for name of groups, then name on users in the portal and finally for normal emails.
    @return a tuple with (cc emails, bcc emails) inside
    """
    sendto_all, sendto_values = _getConfiguration(object)
    acl_users = getToolByName(object, 'acl_users')
    mtool = getToolByName(object, 'portal_membership')
    putils = getToolByName(object, 'plone_utils')

    emails = []
    emails_bcc = []
    if sendto_all:
        # users = acl_users.getUsers() # Dor not use for Plone 2.5 compatibility
        users = mtool.listMembers()
        emails_bcc.extend([m.getProperty('email') for m in users if putils.validateSingleEmailAddress(m.getProperty('email'))])
    for entry in sendto_values:
        if entry.startswith("#"):
            # I also support comment inside the emails data
            continue
        inBcc = False
        if entry.endswith("|bcc") or entry.endswith("|BCC"):
            entry = entry[:-4]
            inBcc = True 
        group = acl_users.getGroupById(entry)
        # 1 - is a group?
        if group:
            if inBcc:
                emails_bcc.extend(_getAllValidEmailsFromGroup(putils, acl_users, group))
            else:
                emails.extend(_getAllValidEmailsFromGroup(putils, acl_users, group))                
            continue
        # 2 - is a member?
        #user = acl_users.getUserById(entry) # BBB: seems not working... only on Plone 2.5?
        user = mtool.getMemberById(entry)
        if user:
            email = user.getProperty('email')
            if putils.validateSingleEmailAddress(email):
                if inBcc:
                    emails_bcc.append(email)
                else:
                    emails.append(email)
            continue
        # 3 - is a valid email address?
        if putils.validateSingleEmailAddress(entry):
            if inBcc:
                emails_bcc.append(entry)
            else:
                emails.append(entry)                
            continue
        # 4 - don't know how to handle this
        object.plone_log( "Can't use the %s info to send notification" % entry)
    emails = set(emails)
    emails_bcc = set(emails_bcc)
    return [x for x in emails if x not in emails_bcc], list(emails_bcc)

def sendMail(object, event):
    """A Zope 3 event for sending e-mail to forum's users"""
    # Check if the product is installed in this instance
    portal_quickinstaller = getToolByName(object, 'portal_quickinstaller')
    if not portal_quickinstaller.isProductInstalled('PloneboardNotify'):
        return
    
    ploneboard_notify_properties = getToolByName(object,'portal_properties')['ploneboard_notify_properties']
    debug_mode = ploneboard_notify_properties.debug_mode
    notify_encode = ploneboard_notify_properties.notify_encode
    portal = getToolByName(object,"portal_url").getPortalObject()
    portal_transforms = getToolByName(object, "portal_transforms")

    send_from = portal.getProperty('email_from_address')
    if send_from and type(send_from)==tuple:
        send_from = send_from[0]
        
    # Conversation or comment?
    conversation = object.getConversation()
    forum = conversation.getForum()

    send_to, send_to_bcc = _getSendToValues(forum)
    if not send_to and not send_to_bcc:
        return
        
    translation_service = getToolByName(object,'translation_service')
    # I use the dummy vars below to make i18ndude works

    dummy = _(u"New comment added on the forum: ")
    msg_sbj = ploneboard_notify_properties.msg_subject
    if not msg_sbj:
        msg_sbj = u"New comment added on the forum: "
    subject = translation_service.utranslate(domain='Products.PloneboardNotify',
                                             msgid=msg_sbj,
                                             default=msg_sbj,
                                             context=object)
    subject+= forum.Title().decode('utf-8')

    dummy = _(u"Message added by: ")
    msg_from = ploneboard_notify_properties.msg_from
    if not msg_from:
        msg_from = u"Message added by: "
    from_user = translation_service.utranslate(domain='Products.PloneboardNotify',
                                          msgid=msg_from,
                                          default=msg_from,
                                          context=object)

    pm = getToolByName(object,'portal_membership')
    if pm.isAnonymousUser():
        fullname = translation_service.utranslate(domain='Products.PloneboardNotify',
                                          msgid="Anonymous",
                                          default="Anonymous",
                                          context=object)
    else:
        member = pm.getAuthenticatedMember()
        fullname = member.getProperty('fullname') or member.getId()
    dummy = _(u"Argument is: ")
    msg_txt = ploneboard_notify_properties.msg_argument
    if not msg_txt:
        msg_txt = u"Argument is: "
    argument = translation_service.utranslate(domain='Products.PloneboardNotify',
                                          msgid=msg_txt,
                                          default=msg_txt,
                                          context=object)

    dummy = _(u"The new message is:")
    msg_txt = ploneboard_notify_properties.msg_mess
    if not msg_txt:
        msg_txt = u"The new message is:"
    new_mess = translation_service.utranslate(domain='Products.PloneboardNotify',
                                          msgid=msg_txt,
                                          default=msg_txt,
                                          context=object)

    # Kupu/Tiny can contains relative URLs
    html_body = object.REQUEST.form['text'].decode('utf-8')
    # match_objs = url_finder.findall(html_body)
    # for match_obj in match_objs:
    #     if match_obj:
    #         all_groups = match_obj.groups()

    here_url = object.absolute_url()
    def fixURL(match):
        """Fix relative URL to absolute ones"""
        value = match.group()
        pos_s = value.find(match_start)+len(match_start)
        pos_e = value.find('"', pos_s+1)
        url = value[pos_s:pos_e]
        if not url.startswith(here_url):
            return value.replace(url, "%s/%s" % (here_url, url))
        return value
  
    html_body = url_finder.sub(fixURL, html_body)

    text = html_template.message % ({'from': from_user + fullname.decode('utf-8'),
                                     'argument': argument + conversation.Title().decode('utf-8'),
                                     'message_intro': new_mess,
                                     'message': html_body,
                                     'url': here_url,
                                     'url_text': here_url,
                                     })
    
    if notify_encode:
        text = text.encode(notify_encode)

    try:
        data_to_plaintext = portal_transforms.convert("html_to_web_intelligent_plain_text", text)
    except:
        # Probably Plone 2.5.x
        data_to_plaintext = portal_transforms.convert("html_to_text", text)
    plain_text = data_to_plaintext.getData()
    
    msg = MIMEMultipart('alternative')
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(plain_text, 'plain', _charset=notify_encode)
    part2 = MIMEText(text, 'html', _charset=notify_encode)

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    mail_host = getToolByName(object, 'MailHost')
    try:
        if debug_mode:
            print "Message subject: %s" % subject
            print "Message text:\n%s" % text
            print "Message sent to %s (and to %s in bcc)" % (", ".join(send_to) or 'no-one',
                                                             ", ".join(send_to_bcc) or 'no-one')
        else:
            try:
                mail_host.secureSend(msg, mto=send_to, mfrom=send_from,
                                     subject=subject, charset=notify_encode, mbcc=send_to_bcc)
            except TypeError:
                # BBB: Plone 2.5 has problem sending MIMEMultipart... fallback to normal plain text email
                mail_host.secureSend(plain_text, mto=send_to, mfrom=send_from,
                                     subject=subject, charset=notify_encode, mbcc=send_to_bcc)                
    except Exception, inst:
        putils = getToolByName(object,'plone_utils')
        putils.addPortalMessage(_(u'Not able to send notifications'))
        object.plone_log("Error sending notification: %s" % str(inst))
