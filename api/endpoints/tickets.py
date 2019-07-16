"""
/tickets endpoint.
"""
import json
import marshmallow as mm
from flask import Blueprint, request
from flask_apispec import doc, marshal_with, use_kwargs

from api.models.db import Ticket, User
from api.endpoints.util.auth import common_params, login_required, admin_required
from api.util import cache

tickets = Blueprint('tickets', __name__)


class TicketSchema(mm.Schema):
    class Meta:
        strict = True

    flight_id = mm.fields.Integer(required=True)


class TicketsSchema(mm.Schema):
    tickets = mm.fields.Nested(TicketSchema, many=True)


@tickets.route('/api/tickets/book', methods=('POST', ))
@doc(params=common_params)
@use_kwargs(TicketSchema(), locations=('json', ))
@login_required
def create(**kwargs):
    """Book a ticket."""
    # user = User.query.filter_by(id=request.user_id)
    # flight = Flight.query.filter_by(id=ticket.flight)
    # try:
    # stripe.Charge.create(customer=user.stripe_id,
    #                      amount=flight.price,
    #                      currency='usd',
    #                      description='Ticket booking')
    ticket = Ticket(**kwargs)
    ticket.paid = True
    ticket.booked_by_id = request.user_id
    ticket.save()
    response = {'message': 'Ticket successfully booked.'}
    # except stripe.CardError as e:
    #     return {'message': str(e)}, 400

    return response, 201


@tickets.route('/api/tickets/<int:user_id>', methods=('GET', ))
@doc(params={**common_params, **cache.cache_params})
@marshal_with(TicketsSchema())
@admin_required
def get_by_user(user_id):
    """Get all tickets booked by user."""
    use_cache = cache.parse_use_cache(request.headers)
    cached_tickets = cache.get_data_from_redis([f'user_{user_id}'])
    if cached_tickets and use_cache:
        tickets = cached_tickets.get(f'user_{user_id}')
        return {'tickets': tickets}, 200

    tickets = Ticket.query.filter_by(booked_by_id=user_id).all()
    if tickets:
        cache.cache_data_in_redis({f'user_{user_id}': [TicketSchema().dump(ticket).data
                                                       for ticket in tickets]})
    return {'tickets': tickets}, 200


@tickets.route('/api/tickets/mine', methods=('GET', ))
@doc(params={**common_params, **cache.cache_params})
@marshal_with(TicketsSchema())
@login_required
def get_mine():
    """Get all tickets booked by user."""
    use_cache = cache.parse_use_cache(request.headers)
    cached_tickets = cache.get_data_from_redis([f'user_{request.user_id}'])
    if cached_tickets and use_cache:
        tickets = cached_tickets.get(f'user_{request.user_id}')
        return {'tickets': tickets}, 200

    tickets = Ticket.query.filter_by(booked_by_id=request.user_id)
    if tickets:
        cache.cache_data_in_redis({f'user_{request.user_id}': [TicketSchema().dump(ticket).data
                                                               for ticket in tickets]})
    return {'tickets': tickets}, 200


@tickets.route('/api/tickets/cancel/<int:ticket_id>', methods=('DELETE', ))
@doc(params=common_params)
@login_required
def cancel(ticket_id):
    """Get flights by route."""
    current_user = User.query.filter_by(id=request.user_id).first()
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    if ticket.booked_by_id == (request.user_id or current_user.is_admin):
        ticket.delete()
    return {'message': 'Ticket successfully cancelled.'}, 200
