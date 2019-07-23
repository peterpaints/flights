"""
Flights application.

"""

import logging

from flask import Flask, request, jsonify
from flask_apispec import FlaskApiSpec
from flask_cors import CORS
from flask_migrate import Migrate

import api.settings
from api.endpoints.healthz import healthz
from api.endpoints.users import users
from api.endpoints.flights import flights
from api.endpoints.routes import routes
from api.endpoints.tickets import tickets
from api.models.db import db

NAME = 'flights'

docs = FlaskApiSpec()


def create_app(config_obj=api.settings, **config_overrides):
    """Instantiate and return a configured flask application.
    (See http://flask.pocoo.org/docs/patterns/appfactories/)

    Defaults are always registered from `thali.settings`, but can be updated via named kwargs.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level=logging.INFO)

    app = Flask(NAME)
    app.config.from_object(config_obj)  # defaults
    app.config.update(config_overrides)

    # Configure db
    with app.app_context():
        db.init_app(app)
        db.create_all()

    Migrate(app, db)

    app.register_blueprint(healthz)
    app.register_blueprint(users)
    app.register_blueprint(flights)
    app.register_blueprint(routes)
    app.register_blueprint(tickets)

    CORS(app, resources={r"/api/*": {'origins': '*'}})

    @app.before_request
    def log_request_body():
        if request.get_data():
            root_logger.info('Request Data: %s', request.json)

    # error handling & reporting
    @app.errorhandler(422)
    def handle_unprocessable_entity(err):
        """Emit a helpful message when client gives args that fail validation.
        https://webargs.readthedocs.io/en/latest/framework_support.html#error-handling
        """
        # webargs attaches additional metadata to the `data` attribute
        try:
            exc = getattr(err, "exc")
        except:
            return jsonify({"messages": err.description}), 422

        if exc:
            messages = exc.messages  # get validations from the ValidationError object
        else:
            messages = ["Invalid request"]
        return jsonify({"messages": messages}), 422

    @app.errorhandler(500)
    def handle_internal_error(err):
        """Handle 500 erros."""
        return jsonify({"message": str(err)}), 500

    @app.errorhandler
    def handle_generic_error(err):
        """Generic error handler. (This one is triggered if no other handler is triggered.)"""
        root_logger.error('Application Exception: {}'.format(err))

    if not app.testing:  # workaround https://github.com/jmcarp/flask-apispec/issues/56 during testing
        # generate Swagger 2.0 documentation for view functions and classes
        docs.init_app(app)
        docs.register_existing_resources()

    return app


def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
