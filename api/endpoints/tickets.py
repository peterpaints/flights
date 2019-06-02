"""
/tickets endpoint.
"""
import marshmallow as mm
from flask import Blueprint, request
from flask_apispec import doc, marshal_with, use_kwargs

from api.models.db import Ticket, User
from api.endpoints.util.auth import common_params, login_required, admin_required

tickets = Blueprint('tickets', __name__)


class TicketSchema(mm.Schema):
    class Meta:
        strict = True

    flight = mm.fields.Integer(required=True)

    @mm.post_load
    def make_ticket(self, data):
        return Ticket(**data)


class TicketsSchema(mm.Schema):
    tickets = mm.fields.Nested(TicketSchema, many=True)


ticket_params = {
    'payment_method': {
        'description': 'Payment Method',
        'in': 'query',
        'type': 'string',
        'options': ['card', 'paypal'],
        'default': 'card',
        'validate': True,
        'required': True
    },
}


@tickets.route('/api/tickets/book', methods=('POST', ))
@doc(params={**common_params, **ticket_params})
@use_kwargs(TicketSchema(), locations=('json', ))
@marshal_with(TicketSchema())
@login_required
def create(ticket):
    """Book a ticket."""
    try:
        ticket.booked_by = request.user_id
        if request.args.get('payment_method') == 'card':
            ticket.paid = True  # stand in for card processing
        ticket.save()
        response = {'message': 'Ticket successfully booked.', 'ticket': ticket}
        return response, 201
    except Exception as e:
        return {'message': str(e)}, 500


@tickets.route('/api/tickets/<int:user_id>', methods=('GET',))
@doc(params=common_params)
@marshal_with(TicketsSchema())
@admin_required
def get_all(user_id):
    """Get all tickets booked by user."""
    try:
        tickets = Ticket.query.filter_by(booked_by=user_id)
        return {'tickets': tickets}, 200
    except Exception as e:
        return {'message': str(e)}, 500


@tickets.route('/api/tickets/mine', methods=('GET',))
@doc(params=common_params)
@marshal_with(TicketsSchema())
@login_required
def get_mine():
    """Get all tickets booked by user."""
    try:
        tickets = Ticket.query.filter_by(booked_by=request.user_id)
        return {'tickets': tickets}, 200
    except Exception as e:
        return {'message': str(e)}, 500


@tickets.route('/api/tickets/cancel/<int:ticket_id>', methods=('DELETE',))
@doc(params=common_params)
@login_required
def cancel(ticket_id):
    """Get flights by route."""
    try:
        current_user = User.query.filter_by(id=request.user_id)
        ticket = Ticket.query.filter_by(id=ticket_id)
        if ticket.booked_by == request.user_id or current_user.is_admin:
            ticket.delete()
        return {'message': 'Ticket successfully cancelled.'}, 200
    except Exception as e:
        return {'message': str(e)}, 500
