import install

install.register_wikid_plugin()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    install.register_wikid_plugin_class(context)
