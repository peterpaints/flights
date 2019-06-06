import os

user = os.getenv('DB_USER', 'postgres')
password = os.getenv('DB_PASSWORD', 'password')
host = os.getenv('DB_HOST', 'postgres')
SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{user}:{password}@{host}:5432/test'
SQLALCHEMY_TRACK_MODIFICATIONS = False
