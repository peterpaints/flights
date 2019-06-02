"""
/flights endpoint.
"""
import marshmallow as mm
from flask import Blueprint, request
from flask_apispec import doc, marshal_with, use_kwargs

from api.models.db import Flight
from api.endpoints.util.auth import common_params, login_required, admin_required

flights = Blueprint('flights', __name__)


class FlightSchema(mm.Schema):
    class Meta:
        strict = True

    origin = mm.fields.Integer(required=True)
    destination = mm.fields.Integer(required=True)
    departure = mm.fields.DateTime(required=True)
    arrival = mm.fields.DateTime(required=True)
    price = mm.fields.Number(required=True)
    capacity = mm.fields.Integer(required=True)
    tickets = mm.fields.List(mm.fields.Integer(), many=True)

    @mm.post_load
    def make_flight(self, data):
        return Flight(**data)


class FlightsSchema(mm.Schema):
    flights = mm.fields.Nested(FlightSchema, many=True)


flight_request_params = {
    'origin': {
        'description': 'Origin',
        'in': 'query',
        'type': 'int',
        'required': False
    },
    'destination': {
        'description': 'Destination',
        'in': 'query',
        'type': 'int',
        'required': False
    },
    'departure': {
        'description': 'Departure Day',
        'in': 'query',
        'type': 'int',
        'required': False
    }
}


@flights.route('/api/flights', methods=('POST', ))
@doc(params=common_params)
@use_kwargs(FlightSchema(), locations=('json', ))
@marshal_with(FlightSchema())
@admin_required
def create(flight):
    """Create flight."""
    try:
        flight.save()
        response = {'message': 'Flight created.', 'flight': flight}
        return response, 200
    except Exception as e:
        return {'message': str(e)}, 500


@flights.route('/api/flights', methods=('GET', ))
@doc(params=common_params)
@marshal_with(FlightsSchema())
@login_required
def get_all():
    """Get all flights."""
    try:
        flights = Flight.query.all()
        return {'flights': flights}, 200
    except Exception as e:
        return {'message': str(e)}, 500


@flights.route('/api/flights/route', methods=('GET', ))
@doc(params={**common_params, **flight_request_params})
@marshal_with(FlightsSchema())
@login_required
def get_by_route():
    """Get flights by route."""
    try:
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        flights = Flight.query.filter_by(origin=origin,
                                         destination=destination).all()
        return {'flights': flights}, 200
    except Exception as e:
        return {'message': str(e)}, 500


@flights.route('/api/flights/<int:origin>', methods=('GET', ))
@doc(params=common_params)
@marshal_with(FlightsSchema())
@login_required
def get_by_origin(origin):
    """Get flights by origin."""
    try:
        flights = Flight.query.filter_by(origin=origin).all()
        return {'flights': flights}, 200
    except Exception as e:
        return {'message': str(e)}, 500


@flights.route('/api/flights/<int:destination>', methods=('GET', ))
@doc(params=common_params)
@marshal_with(FlightsSchema())
@login_required
def get_by_destination(destination):
    """Get flights by destination."""
    try:
        flights = Flight.query.filter_by(destination=destination).all()
        return {'flights': flights}, 200
    except Exception as e:
        return {'message': str(e)}, 500
