# Set security group access rules from file. This allows version control on the rules
# As well as comments to be attached per line. Does not yet understand port ranges
def set_security_groups (ec2, file_to_use):
    all_groups = ec2.get_all_security_groups()
    rules_dictionary = parse_security_group_config(file_to_use)

    for group in all_groups:
        if group.id not in rules_dictionary:
            print "Could not find any rules for group %s, so not revoking existing ones" % group.id
        else:
            # Remove all existing rules
            for rule in group.rules:
                for grant in rule.grants:
                    group.revoke(ip_protocol=rule.ip_protocol, from_port=rule.from_port, to_port=rule.to_port, cidr_ip=grant)

        # Add back new rules
        if group.id not in rules_dictionary:
            print "Could not find any rules for group %s, so none to add" % group.id
        else:
            for rule in rules_dictionary[group.id]:
                group.authorize(rule[0], rule[1], rule[1], rule[2])

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# There's no error checking on this function at all, yet
def parse_security_group_config(file_to_read):
    FH = open(file_to_read, 'r')
    rule_dict = {}

    section_title=''
    for line in FH.readlines():
        if not line.strip():
            continue

        protocols = ''
        ports = ''
        ips = ''

        usable_line = line.split('#')[0] # Grab everythin before the comments start
        if (usable_line != ''):               # Skip empty lines
            if (usable_line[0] == '['):
                # Line is a [security group] section header
                section_title = usable_line.split('[')[1].split(']')[0]
                rule_dict[section_title] = []
            else:
                # Line is a rule for the current group
                data_array = usable_line.split()
                protocol = data_array[0]
                ports = data_array[1]
                ips = data_array[2]
                rule_dict[section_title].append([protocol, ports, ips])
    return rule_dict
