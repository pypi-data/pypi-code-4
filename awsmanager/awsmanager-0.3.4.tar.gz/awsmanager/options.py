import ConfigParser, boto, sys
from optparse import OptionParser, OptionGroup
from awsmanager import snapshots, utils, reports, instances, iam

def options_sanity_check(opts):
    if opts['pause_instance'] and opts['unpause_instance']:
          print 'Cannot both pause and unpause an instance!'
          sys.exit(1)
    if opts['instance_name'] and opts['instance_id']:
          print 'Cannot look for both id and a name at same time'
          sys.exit(1)


    if (not opts['all_regions'] and not opts['region']) and not opts['print_policies']:
          print 'You must use -r to specify a region, or use -a to operate on all regions'
          sys.exit(1)

    all_region_names = []
    for region in boto.ec2.regions():
        all_region_names.append(region.name)
    if opts['region'] and (opts['region'] not in all_region_names):
          print 'No such region avilable. Possible options:'
          for region in boto.ec2.regions():
              print region.name
          sys.exit(1)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def process_options(ec2, opts):
    options_sanity_check(opts)

    if (opts['tags']):
        utils.check_tags(ec2, opts)

    elif (opts['termination_protection']):
        instances.enable_termination_protection(ec2, opts)

    elif (opts['associate_eips']):
        instances.associate_eips(ec2)

    elif (opts['snapshots']):
        snapshots.take_snapshots(ec2, opts)

    elif (opts['check_snapshots']):
        snapshots.check_snapshots(ec2, opts)

    elif (opts['purge_snapshots']):
        snapshots.purge_old_snapshots(ec2, opts)
        snapshots.purge_extra_snapshots(ec2, opts)

    elif (opts['unpause_instance']):
        instances.unpause_instance(ec2, opts)

    elif (opts['pause_instance']):
        instances.pause_instance(ec2, opts)

    elif (opts['print_policies']):
        iam.print_all_policies()

    # W.I.P
    #elif (ops.security_groups != None):
    #    security_groups.set_security_groups(ec2, file_to_use=ops.security_groups)
    #elif (ops.owner_email != None):
    #    reports.do_ownership_reports(admin_email=ops.owner_email, confOps)
    else:
        print 'Error in cmdline options, use --help for more information'
        sys.exit(1)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def read_config_file(command_options):
    config_options = {}
    config = ConfigParser.RawConfigParser()
    try:
        config.read(command_options.config_file)
        for item in ['syslog_level', 'snapshot_identifier']:
            config_options[item] = config.get('main', item)

        for item in ['snapshot_age_limit', 'startup_sleep_seconds', 'snapshot_max_revisions']:
              config_options[item] = config.getint('main', item)

        config_options['tags_in_use'] = config.get('main', 'tags_in_use').split(',')
    except:
        print "Error parsing configuration file [%s]"  % command_options.config_file
        print traceback.print_exc()
        sys.exit(1)
    return config_options

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def parse_options():
    parser = OptionParser()

    snapshot_group = OptionGroup(parser, 'Snapshot options')
    snapshot_group.add_option('-s', '--do_snapshot', dest='snapshots', action='store_true', default=False, help='Take snapshots of any instances set to do so')
    snapshot_group.add_option('--check_snapshots', dest='check_snapshots', action='store_true', default=False, help='Check snapshots are happening')
    snapshot_group.add_option('-p', '--do_snapshot_purge', dest='purge_snapshots', action='store_true', default=False, help='Purge old snapshots')

    meta_group = OptionGroup(parser, 'Metadata options')
    meta_group.add_option('--check_tags', dest='tags', action='store_true', default=False, help='Check tag usage')
    #meta_group.add_option('-m', '--owner_email', dest='owner_email', help='Send out email reports on resource usage', metavar='<admin email>')
    #meta_group.add_option('-g', '--groups', dest='security_groups', help='Update secruity groups from file', metavar='<file path>')

    instance_group = OptionGroup(parser, 'Instance options')
    instance_group.add_option('-o', '--instance_on', dest='unpause_instance', default=False, action='store_true', help='Unpause instance')
    instance_group.add_option('-O', '--instance_off', dest='pause_instance', default=False, action='store_true', help='Pause instance')
    instance_group.add_option('-n', '--instance_name', dest='instance_name', help='Instance name tag')
    instance_group.add_option('-i', '--instance_id', dest='instance_id', help='Instance identifier')
    instance_group.add_option('-t', '--termination_protection', dest='termination_protection', default=False, action='store_true', help='Enable termination protection')
    instance_group.add_option('--associate_eips', dest='associate_eips', action='store_true', default=False, help='Associate any hanging elastic IPs')

    misc_group = OptionGroup(parser, 'Misc options')
    misc_group.add_option('-c', '--config_file', dest='config_file', default='/etc/aws_manager.cfg', help='Config file to use')
    misc_group.add_option('--debug', dest='debug', action='store_true', default=False, help='Enable debugging output')

    scope_group = OptionGroup(parser, 'Region scoping options')
    scope_group.add_option('-r', '--region', dest='region', default='', help='Region, default is to operate sequentially upon all regions', metavar='<region>')
    scope_group.add_option('-a', '--all_regions', dest='all_regions', default=False, action='store_true', help='Operate across all regions')

    iam_group = OptionGroup(parser, 'IAM service options')
    iam_group.add_option('--print_iam_policies', dest='print_policies', action='store_true', default=False, help='Print to console all IAM policies')


    parser.add_option_group(snapshot_group)
    parser.add_option_group(meta_group)
    parser.add_option_group(instance_group)
    parser.add_option_group(misc_group)
    (command_options, args) = parser.parse_args()
    return command_options
