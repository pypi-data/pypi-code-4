import clouddns
import gflags
import wnyc_dns.common

FLAGS = gflags.FLAGS

gflags.DEFINE_string('username',
                     None,
                     'Your rackspace username')
gflags.DEFINE_string('apikey', 
                     None,
                     'Your rackspace API key')

def connection():
    return clouddns.connection.Connection(FLAGS.username, FLAGS.apikey)

def update_ip_addresses(old, new, *excludes):
    dns = connection()
    for domain in dns.get_domains():
        for record in domain.get_records():
            if (record.type, record.data) == ('A', old):
                for exclude in excludes:
                    if record.name.startswith(exclude):
                        continue
                if FLAGS.live:
                    print "Changing", 
                    record.update(data=new)
                else:
                    print "Would have changed", 
                print domain.name, record.name, "from", old, "to", new

COMMANDS = {'update_ip_addresses': update_ip_addresses}

def main(argv=None, stdin=None, stdout=None, stderr=None):
    import sys
    argv = argv or sys.argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        argv = FLAGS(argv)[1:]
        if  argv[0] not in COMMANDS:
            stderr.write("%s\\nUsage: %s update_id_addresses\\n%s\n" %
                         (e, sys.argv[0], FLAGS))
            return 1
    except gflags.FlagsError, e:
        stderr.write("%s\\nUsage: %s update_id_addresses\\n%s\n" %
                     (e, sys.argv[0], FLAGS))
        return 1
    
    COMMANDS[argv[0]](*argv[1:])
    
