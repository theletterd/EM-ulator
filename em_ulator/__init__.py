from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=False)

    from . import models
    with app.app_context():
        db.init_app(app)
        db.create_all()
        models.TicketState.initialise_ticket_states()

    from em_ulator import blueprints
    app.register_blueprint(blueprints.home_app)

    return app
