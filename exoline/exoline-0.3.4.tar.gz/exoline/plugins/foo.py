'''Print foo

Usage:
    exo [options] foo'''
class Plugin():
    def command(self):
        return 'foo'
    def run(self, cmd, args, options):
        cik = options['cik']
        rpc = options['rpc']
        ExoException = options['exception']
        if cmd == 'foo':
            print 'foo'
