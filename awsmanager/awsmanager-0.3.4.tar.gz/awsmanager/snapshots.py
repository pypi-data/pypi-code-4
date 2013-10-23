import dateutil.parser, time
from awsmanager import utils

# N.B: this does not currently check that the snapshots are recent or otherwise usable
def check_snapshots (ec2, opts):
    print "Checking snapshots exist..."
    instances = utils.get_instance_objs(ec2, opts, filterDict={'tag:AutoSnapshot': 'Yes'})
    if instances == None:
        return None

    # Create list of all volumes attached to instances which are flagged as needing snapshots
    for instance in instances:
        vols_to_snapshot = []
        block_map = instance.block_device_mapping
        for blockname, block_obj in block_map.iteritems():
            if block_obj.volume_id not in vols_to_snapshot:
                vols_to_snapshot.append(block_obj.volume_id)

    # Create a list of all snapshots that exist
    all_snapshots = ec2.get_all_snapshots(owner='self')
    snapshot_volume_ids = []
    for snapshot in all_snapshots:
        if snapshot.volume_id not in snapshot_volume_ids:
            snapshot_volume_ids.append(snapshot.volume_id)

    if vols_to_snapshot:
        # Compare the two lists
        error_count = 0
        for vol in vols_to_snapshot:
            if vol not in snapshot_volume_ids:
                error_count += 1
                print "Error: Volume %s appears to have no snapshot for it !" % vol
        if error_count == 0:
            print 'All volumes have snapshots that should'
    else:
        print "No volumes seem to have snapshots in this region"

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def take_snapshots (ec2, opts):
    instances = utils.get_instance_objs(ec2, opts, filterDict={'tag:AutoSnapshot': 'Yes'})        # We only snapshot a volume if the instance is tagged as such
    if instances == None:
        return None

    print "Taking snapshots of volumes for matching machines that are tagged with 'AutoSnapshot' = 'Yes'"

    volume_id_list = []
    for instance in instances:
        for name, device in instance.block_device_mapping.iteritems():
            volume_id_list.append(device.volume_id)                 # Gather a list of volume ids for volumes attached to such tagged instances

    volume_objs = ec2.get_all_volumes(volume_ids=volume_id_list)    # Get a list of all volume objects that match our list of ids
    for volume_obj in volume_objs:
        print "Creating snapshot for %s" % volume_obj.id
        description_string = "Automatic %s triggered snapshot of [%s]" % (opts['snapshot_identifier'], volume_obj.id)
        if 'Name' in volume_obj.tags:
            description_string += ' for %s' % (volume_obj.tags['Name'])
        volume_obj.create_snapshot(description_string)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def purge_extra_snapshots(ec2, opts):
    print "\nPurging unneeded additional snapshots..."
    all_snapshots = ec2.get_all_snapshots(owner='self')

    all_automated_snapshots = []
    for snapshot in all_snapshots:
        if "Automatic %s triggered snapshot" % opts['snapshot_identifier'] in snapshot.description:
            all_automated_snapshots.append(snapshot)

    volume_count={}
    for snapshot in all_automated_snapshots:
        if snapshot.volume_id not in volume_count:
            volume_count[snapshot.volume_id] = 1
        else:
            volume_count[snapshot.volume_id] += 1

    for volume_id, count in volume_count.items():
        if count > opts['snapshot_max_revisions']:
            snapshot_time_tuples = []
            for snapshot in [snapshot for snapshot in all_automated_snapshots if snapshot.volume_id == volume_id]:
                dateObj = dateutil.parser.parse(snapshot.start_time)
                start_time_as_epoch = int(dateObj.strftime("%s"))
                snapshot_time_tuples.append((snapshot, start_time_as_epoch))

            # Pretty sure the snapshots are sorted by time as default, but just incase they aren't.
            snapshot_time_tuples = sorted(snapshot_time_tuples, key=lambda snapshot: snapshot[1])

            # Grab the slice of the oldest snapshots, from 0 to 'snapshot_max_revisions' from the end of the list
            for snapshot_time_tuple in snapshot_time_tuples[:(-1 * opts['snapshot_max_revisions'])]:
                print 'Deleting snapshot [%s] of volume [%s] for being beyond max revisions of [%s]' % (snapshot_time_tuple[0].id, snapshot_time_tuple[0].volume_id, opts['snapshot_max_revisions'])
                snapshot_time_tuple[0].delete()
        else:
            print 'Not enough snapshot revisions of volume [%s] found to consider purging some of them' % snapshot.volume_id

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def purge_old_snapshots (ec2, opts):
    print "Purging old snapshots..."
    all_snapshots = ec2.get_all_snapshots(owner='self')

    for snapshot in [snapshot for snapshot in all_snapshots if "Automatic %s triggered snapshot" % opts['snapshot_identifier'] in snapshot.description]:
        dateObj = dateutil.parser.parse(snapshot.start_time)
        start_time_as_epoch = int(dateObj.strftime("%s"))
        time_now_as_epoch = int(time.time())
        age_in_seconds =  time_now_as_epoch - start_time_as_epoch
        if (age_in_seconds > opts['snapshot_age_limit']):
            print "Old snapshot found: Snapshot %s of %s is %s seconds old. " \
            "The limit is %s. Purging this snapshot now..." % (snapshot.id, snapshot.volume_id, age_in_seconds, opts['snapshot_age_limit'])
            snapshot.delete()
        else:
            print "Snapshot [%s] of [%s] is not old enough [%s seconds]" % (snapshot.id, snapshot.volume_id, age_in_seconds)
