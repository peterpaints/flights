"""
/flights endpoint.
"""
import marshmallow as mm
from flask import Blueprint, request, abort
from flask_apispec import doc, marshal_with, use_kwargs
from sqlalchemy import and_
from datetime import datetime, timedelta

from api.endpoints.tickets import TicketSchema
from api.endpoints.util.auth import common_params, login_required, admin_required
from api.models.db import Flight

flights = Blueprint('flights', __name__)


class FlightSchema(mm.Schema):
    class Meta:
        strict = True

    origin_id = mm.fields.Integer(required=True)
    destination_id = mm.fields.Integer(required=True)
    departure = mm.fields.DateTime(required=True)
    arrival = mm.fields.DateTime(required=True)
    price = mm.fields.Number(required=True)
    capacity = mm.fields.Integer(required=True)
    tickets = mm.fields.Nested(TicketSchema, many=True)


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

date_range_params = {
    'from': {
        'description': 'start date e.g. 2019-07-19T00:00:00',
        'in': 'query',
        'type': 'string',
        'format': 'date-time',
        'required': False
    },
    'to': {
        'description': 'end date e.g. 2019-07-19T00:00:00',
        'in': 'query',
        'type': 'string',
        'format': 'date-time',
        'required': False
    }
}


@flights.route('/api/flights', methods=('POST', ))
@doc(params=common_params)
@use_kwargs(FlightSchema().fields, locations=('json', ))
@admin_required
def create(**kwargs):
    """Create flight."""
    flight = Flight(**kwargs)
    flight.save()
    response = {'message': 'Flight created.'}
    return response, 201


@flights.route('/api/flights', methods=('GET', ))
@doc(params={**common_params, **date_range_params})
@login_required
def get_all():
    """Get all flights."""
    from_str = request.args.get('from')
    to_str = request.args.get('to')
    try:
        if not from_str:
            from_date = datetime.today()
        else:
            from_date = datetime.strptime(from_str, '%Y-%m-%dT%H:%M:%S')

        if not to_str:
            to_date = from_date + timedelta(days=7)
        else:
            to_date = datetime.strptime(to_str, '%Y-%m-%dT%H:%M:%S')
    except Exception as exc:
        abort(422, str(exc))

    flights = Flight.query.filter(
        and_(Flight.departure >= from_date, Flight.arrival <= to_date)).all()
    # FIXME: return {'flights': flights}, 200
    # For some reason that doesn't work, even though
    # it works in every other endpoint. E.g. L126
    # ¯\_(ツ)_/¯
    return {
        'flights': [FlightSchema().dump(flight).data for flight in flights]
    }, 200


@flights.route('/api/flights/route', methods=('GET', ))
@doc(params={**common_params, **flight_request_params})
@marshal_with(FlightsSchema())
@login_required
def get_by_route():
    """Get flights by route."""
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    flights = Flight.query.filter_by(origin_id=origin,
                                     destination_id=destination).all()
    return {'flights': flights}, 200


@flights.route('/api/flights/origin/<int:origin>', methods=('GET', ))
@doc(params=common_params)
@marshal_with(FlightsSchema())
@login_required
def get_by_origin(origin):
    """Get flights by origin."""
    flights = Flight.query.filter_by(origin_id=origin).all()
    return {'flights': flights}, 200


@flights.route('/api/flights/destination/<int:destination>', methods=('GET', ))
@doc(params=common_params)
@marshal_with(FlightsSchema())
@login_required
def get_by_destination(destination):
    """Get flights by destination."""
    flights = Flight.query.filter_by(destination_id=destination).all()
    return {'flights': flights}, 200
