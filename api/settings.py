"""
Flask application default settings.

All uppercase variables in this entire file are set as
default Flask app config upon app creation.

"""
import os
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

file_plugin = MarshmallowPlugin()

APISPEC_SPEC = APISpec(
    title="Flights API",
    version="v1",
    openapi_version="2.0",
    plugins=[file_plugin],
)
APISPEC_SWAGGER_URL = '/api/swagger.json'
APISPEC_SWAGGER_UI_URL = '/api/'
APISPEC_TITLE = 'flights'

user = os.getenv('DB_USER', 'postgres')
password = os.getenv('DB_PASSWORD', 'password')
host = os.getenv('DB_HOST', 'postgres')
SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{user}:{password}@{host}:5432/flights'
SQLALCHEMY_TRACK_MODIFICATIONS = False
