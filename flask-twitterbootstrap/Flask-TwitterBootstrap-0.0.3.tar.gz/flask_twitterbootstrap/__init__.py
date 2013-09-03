from flask import Blueprint, flash


class Bootstrap(Blueprint):
    def __init__(self, app):
        super(Bootstrap, self).__init__(
            'bootstrap', __name__, template_folder='templates'
        )
        app.register_blueprint(self)


def success(msg):
    flash(msg, 'success')
