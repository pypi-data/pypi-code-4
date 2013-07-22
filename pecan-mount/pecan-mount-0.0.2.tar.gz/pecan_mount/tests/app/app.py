from pecan import make_app


def setup_app(config):

    return make_app(
        config.app.root,
        logging         = getattr(config, 'logging', {}),
        debug           = False,
        force_canonical = True,
    )

