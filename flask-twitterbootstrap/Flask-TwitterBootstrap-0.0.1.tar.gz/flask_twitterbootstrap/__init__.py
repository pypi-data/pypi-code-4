from flask import Blueprint

bootstrap = Blueprint('bootstrap', __name__, template_folder='templates')


def Bootstrap(app):
    app.register_blueprint(bootstrap)
