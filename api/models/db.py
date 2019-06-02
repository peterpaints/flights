import os
import re
from datetime import datetime, timedelta

import jwt
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

SECRET = os.getenv('SECRET', 'secret')


class Base(object):
    id = db.Column(db.Integer, primary_key=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime(timezone=True),
                           onupdate=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean(), default=False, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model, Base):
    """Define the users' table."""

    __tablename__ = 'users'

    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    tickets = db.relationship('Ticket',
                              order_by='Ticket.id',
                              backref='users',
                              cascade='all, delete-orphan',
                              lazy='dynamic')
    photos = db.relationship('Photo',
                             order_by='Photo.id',
                             backref='users',
                             cascade='all, delete-orphan',
                             lazy='dynamic')

    def __init__(self, email, password, is_admin=False):
        """Initialize the user with an email and a password."""
        self.email = email
        self.password = self.set_password(password)
        self.is_admin = is_admin

    @db.validates('email')
    def validate_email(self, key, email):
        if not email:
            raise AssertionError('No email provided')

        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise AssertionError('Provided email is not an email address')

        return email

    def set_password(self, password):
        if not password:
            raise AssertionError('Password not provided')

        if not re.match(r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}", password):
            raise AssertionError('Your password should contain at least one \
                                  number, one lowercase, one uppercase letter \
                                  and at least six characters')

        return Bcrypt().generate_password_hash(password).decode()

    def is_registered_password(self, password):
        """Check the password against its hash."""
        return Bcrypt().check_password_hash(self.password, password)

    def generate_token(self, user_id):
        """Generate the access token."""
        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=1440),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(payload,
                                    SECRET,
                                    algorithm='HS256')
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decode the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, SECRET)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


class Photo(db.Model, Base):
    """Define the photos table."""

    __tablename__ = 'photos'

    name = db.Column(db.String(255), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey(User.id))


class Route(db.Model, Base):
    """Define the routes table."""

    __tablename__ = 'routes'

    city = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    arrivals = db.relationship('Flight',
                               order_by='Flight.id',
                               backref='route_arrivals',
                               cascade='all, delete-orphan',
                               foreign_keys='Flight.destination',
                               lazy='dynamic')
    departures = db.relationship('Flight',
                                 order_by='Flight.id',
                                 backref='route_departures',
                                 cascade='all, delete-orphan',
                                 foreign_keys='Flight.origin',
                                 lazy='dynamic')

    def __repr__(self):
        return "<Route: {}>".format(self.city, self.country)


class Flight(db.Model, Base):
    """Define the flights table."""

    __tablename__ = 'flights'

    capacity = db.Column(db.Numeric(precision=3, asdecimal=False), nullable=False)
    origin = db.Column(db.Integer, db.ForeignKey(Route.id), nullable=False)
    destination = db.Column(db.Integer,
                            db.ForeignKey(Route.id),
                            db.CheckConstraint('origin <> destination'),
                            nullable=False)
    departure = db.Column(db.DateTime(timezone=True))
    arrival = db.Column(db.DateTime(timezone=True),
                        db.CheckConstraint('arrival > departure'))
    price = db.Column(db.Numeric, nullable=False)
    tickets = db.relationship('Ticket',
                              order_by='Ticket.id',
                              backref='flights',
                              cascade='all, delete-orphan',
                              lazy='dynamic')

    def __repr__(self):
        return "<Flight {}: {} {} >".format(self.id, self.origin, self.destination)


class Ticket(db.Model, Base):
    """Define the tickets table."""

    __tablename__ = 'tickets'

    flight = db.Column(db.Integer, db.ForeignKey(Flight.id))
    paid = db.Column(db.Boolean, default=False)
    booked_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        return "<Ticket for flight {}: departing {} and arriving {} >".format(
            self.flight.origin.city, self.flight.destination.city)
