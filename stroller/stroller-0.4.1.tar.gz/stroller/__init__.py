

def plugme(app_config, options):
    """
    tgext.pluggable entry point.

    This will adapt stroller to be compatible with
    the tgext.pluggable expected pluggable application layout.
    """

    import stroller, stroller.helpers
    from stroller.model.core import init_stroller_model, setup_stroller_database

    UserClass = app_config.model.User
    GroupClass = app_config.model.Group
    Declarative = app_config.model.DeclarativeBase
    DBSession = app_config.DBSession

    app_config.model.StrollerProduct, \
    app_config.model.StrollerProductInfo, \
    app_config.model.StrollerCategory, \
    app_config.model.StrollerOrder, \
    app_config.model.StrollerOrderItem = init_stroller_model(DBSession, Declarative, UserClass, GroupClass)

    #As tgext.pluggable expects a RootController to exist rename StrollerController to RootController
    def adapt_stroller_controller(app):
        from stroller.controllers.ecommerce import StrollerController
        import stroller.controllers
        stroller.controllers.RootController = StrollerController
        return app
    app_config.register_hook('after_config', adapt_stroller_controller)

    #As tgext.pluggable expects a bootstrap module to be available to initialize the
    #database we create a fake one to call setup_stroller_database
    class bootstrap(object):
        @staticmethod
        def bootstrap(command, conf, vars):
            return setup_stroller_database(DBSession, Declarative, UserClass, GroupClass)
    stroller.bootstrap = bootstrap

    return dict(appid='shop', global_helpers=True)