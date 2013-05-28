
# Sample Python module to use python plugin

import collectd

#== Our Own Functions go here: ==#
def configure(ObjConfiguration):
        collectd.info('Configuring Stuff')

def init():
        collectd.info('initing stuff')

def read(input_data=None):
#       collectd.error('error message!')
#       collectd.warning('warning message!')
#       collectd.notice('notice message!')
#       collectd.info('info message!')
#       collectd.debug('debug message!')

        #collectd.info('input_data is: ' + str(input_data))

        metric = collectd.Values()
        metric.plugin = 'python_plugin_test'
        metric.type = 'gauge'
        metric.values = [100]
        metric.host = 'OverwritenHostname'

        #collectd.info('metric to dispatch is: ' + str(metric))

        metric.dispatch()

def write(vl, data=None):
        collectd.info('------------------------------------------------')
        collectd.info('write message: ' + str(vl))

        for i in vl.values:
                collectd.info( "%s (%s): %f" % (vl.plugin, vl.type, i) )

def shutdown():
        collectd.info('python plugin shutting down')

#== Hook Callbacks, Order is important! ==#
collectd.register_config(configure)
collectd.register_init(init)
collectd.register_read(read)
collectd.register_write(write)
collectd.register_shutdown(shutdown)

