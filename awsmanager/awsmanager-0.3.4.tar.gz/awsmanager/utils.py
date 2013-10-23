
def get_instance_objs (ec2, opts, filterDict={}):
    if opts['instance_name']:
        filterDict={'tag:Name': opts['instance_name']}
    elif opts['instance_id']:
        filterDict={'instance-id': opts['instance_id']}

    reservations = ec2.get_all_instances(filters=filterDict)

    try:
        instance = reservations[0].instances[0]
    except IndexError as e:
        return None

    all_instances = []
    for reservation in reservations:
        for instance in reservation.instances:
            all_instances.append(instance)
    return all_instances

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def instance_to_name (ec2, instance_id):
    ins_to_name_dict={}
    for tag in ec2.get_all_tags():
        if ((tag.res_type == 'instance') and (tag.name == 'Name')):
            ins_to_name_dict[tag.res_id] = tag.value
    if instance_id in ins_to_name_dict:
        return ins_to_name_dict[instance_id]
    else:
        return 1

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def name_to_instance (ec2, name_to_find):
    name_to_ins_dict={}
    for tag in ec2.get_all_tags():
        if ((tag.res_type == 'instance') and (tag.name == 'Name')):
                name_to_ins_dict[tag.value] = tag.res_id
    if name_to_find in name_to_ins_dict:
        return name_to_ins_dict[name_to_find]
    else:
        return 1

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def region_instances (ec2):
    instance_array = []

    reservations = ec2.get_all_instances()
    for reservation in reservations:
        for instance in reservation.instances:
            instance_array.append(instance)
    return instance_array

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def compile_instance_lists():
    all_global_instances = []
    regions = boto.ec2.regions()
    for region in regions:
        ec2 = region.connect()
        instances = region_instances(ec2)
        if instances:
            all_global_instances.append(instances)
    return all_global_instances

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def check_tags (ec2, opts):
    print "Checking all expected tags are present on all instances..."
    tag_dict={}
    i_to_name_dict={}
    for tag in ec2.get_all_tags():
        if (tag.res_type == 'instance'):
            if tag.res_id in tag_dict:
                tag_dict[tag.res_id].append(tag.name)
            else:
                tag_dict[tag.res_id]=[tag.name]

    for ins, tag_list in tag_dict.iteritems():
        for tag_in_use in opts['tags_in_use']:
            if tag_in_use not in tag_list:
                print "Instance: \"%s\" does not have tag \"%s\"" % (instance_to_name(ec2, ins), tag_in_use)
    print "Done"
