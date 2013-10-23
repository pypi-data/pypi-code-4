import time, sys
import utils

def enable_termination_protection(ec2, opts):
    instances = utils.get_instance_objs(ec2, opts)
    if instances == None:
        print 'No instance not found in this region'
        return None

    for instance in instances:
        if 'elasticbeanstalk:environment-name' in instance.tags:
            print 'Refusing to enable termination protection on an elastic beanstalk instance %s' % instance.id
        else:
            if not ec2.get_instance_attribute(instance.id,'disableApiTermination')['disableApiTermination']:
                print 'Enabling termination protection on instance [%s]' % instance.id
                ec2.modify_instance_attribute(instance.id,'disableApiTermination',True)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def pause_instance (ec2, opts):
    instances = utils.get_instance_objs(ec2, opts)

    if instances == None:
        print 'No instance not found in this region'
        return None

    instance_ids=[]
    for instance in instances:
        instance_ids.append(instance.id)
    print 'Instance(s) found in this region, stopping...'
    ec2.stop_instances(instance_ids)
    print 'Instance(s) should now be in the process of stopping'

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def unpause_instance (ec2, opts):
    instances = utils.get_instance_objs(ec2, opts)
    if instances == None:
        print 'Instance not found in this region'
        return None

    instance_ids=[]
    for instance in instances:
        instance_ids.append(instance.id)
    print "Starting instances: %s" % instance_ids
    ec2.start_instances(instance_ids)
    print 'Sleeping for [%s] seconds to allow time for instance(s) to start... ' % opts['startup_sleep_seconds']
    time.sleep(opts['startup_sleep_seconds'])
    associate_eips(ec2)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def associate_eips (ec2):
    # Build list of instance objects for running instances
    filterDict={'instance-state-name': 'running'}
    running_reservations = ec2.get_all_instances(filters=filterDict)
    matching_instances = []
    for res in running_reservations:
        instance = res.instances[0]
        if (('Name' in instance.tags) and ('EIP' in instance.tags)):    # If instance does not have a Name or EIP, we will ignore it
            matching_instances.append(instance)

    # Build list of unassocaiated eIPs -- it might be possible to filter the get_all_addresses call directly
    all_address_objs = ec2.get_all_addresses()
    hanging_address_list = []
    for address_obj in all_address_objs:
        if (address_obj.instance_id == ''):
            hanging_address_list.append(address_obj)

    # Compare the two lists and link addresses where possible
    for address_obj in hanging_address_list:
        for instance in matching_instances:
            if (instance.tags['EIP'] == address_obj.public_ip):
                print "Linking ip: %s back to instance \"%s\" [%s]" % (address_obj.public_ip, instance.tags['Name'], instance.id)
                address_obj.associate(instance.id)
