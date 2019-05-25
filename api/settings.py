"""
Flask application default settings.

All uppercase variables in this entire file are set as
default Flask app config upon app creation.

"""

APISPEC_SWAGGER_URL = '/api/swagger.json'
APISPEC_SWAGGER_UI_URL = '/api/'
APISPEC_TITLE = 'flights'

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/flights'
SQLALCHEMY_TRACK_MODIFICATIONS = False
