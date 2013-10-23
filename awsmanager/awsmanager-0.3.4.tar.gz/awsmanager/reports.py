import utils

def do_ownership_reports(admin_email):
    instance_dict= {}
    untagged_instances = []

    all_instances = utils.compile_instance_lists()
    for instances in all_instances:
        for instance in instances:
            if ('Owner' in instance.tags):
                owner = instance.tags['Owner']
                if owner not in instance_dict:
                    instance_dict[owner] = []
                instance_dict[owner].append(instance)
            else:
                untagged_instances.append(instance)

    for owner, instances in instance_dict.iteritems():
        if instances:
            send_email(owner, admin_email, prepare_owner_email(instances), confOps)
    send_email(admin_email, '', prepare_admin_email(instance_dict, untagged_instances), confOps)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def prepare_owner_email(instances):
    msg = 'This is a friendly reminder that the following instances at amazon EC2 have been identified as being under your responsibility. '
    msg += '\n\nPlease review the below list of instances, and take action if any are unexpected.\n'
    msg += '\n{0:25} {1:10} {2:10} {3:20} {4:10}'.format('Name', 'ID', 'State', 'Placement', 'Size')
    msg += '\n'+('-'*80)+'\n'
    for instance in instances:
        msg += "{0:25} {1:10} {2:10} {3:20} {4:10}\n".format(instance.tags['Name'], instance.id, instance.state, instance.placement, instance.instance_type)
    return msg

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def prepare_admin_email(instance_dict, untagged_instances):
    msg = 'EC2 Ownership information'
    msg += '\n'+('-'*100)+'\n'
    for owner, instances in instance_dict.iteritems():
        for instance in instances:
            msg += "{0:30} {1:25} {2:10} {3:10} {4:20} {5:10}\n".format(owner, instance.tags['Name'], instance.id, instance.state, instance.placement, instance.instance_type)
    msg += '\n'+('-'*100)+'\n'+('-'*100)
    msg += '\nUNTAGGED INSTANCES:\n\n'
    for instance in untagged_instances:
        msg += "{0:25} {1:10} {2:10} {3:20} {4:10}\n".format(instance.tags['Name'], instance.id, instance.state, instance.placement, instance.instance_type)
    return msg

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def send_email(address, admin_email, email_body, confOps):
    if (address == admin_email): # The admin gets their own email, so don't bother sending them an owner one also
        return
    subject = 'Amazon EC2 resource ownership information (automated email)'
    import string
    email = string.join((
        "From: %s" % admin_email,
        "To: %s" % address,
        "Subject: %s" % subject,
        "",
        email_body
        ), "\r\n")
    server = smtplib.SMTP(confOps['smtp_server'])
    server.sendmail(admin_email, address, email)
    server.quit()
