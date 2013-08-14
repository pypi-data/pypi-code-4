from pas.plugins.osiris.plugin import OsirisHelper

TITLE = 'Osiris plugin (pas.plugins.osiris)'


def isNotThisProfile(context):
    return context.readDataFile("osiris_marker.txt") is None


def _addPlugin(pas, pluginid='pasosiris'):
    installed = pas.objectIds()
    if pluginid in installed:
        return TITLE + " already installed."
    plugin = OsirisHelper(pluginid, title=TITLE)
    pas._setObject(pluginid, plugin)
    plugin = pas[plugin.getId()]  # get plugin acquisition wrapped!
    for info in pas.plugins.listPluginTypeInfo():
        interface = info['interface']
        if not interface.providedBy(plugin):
            continue
        pas.plugins.activatePlugin(interface, plugin.getId())
        # In case we want to move it to the top
        # pas.plugins.movePluginsDown(
        #     interface,
        #     [x[0] for x in pas.plugins.listPlugins(interface)[:-1]],
        # )


def setupPlugin(context):
    if isNotThisProfile(context):
        return
    site = context.getSite()
    pas = site.acl_users
    _addPlugin(pas)
