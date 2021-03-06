"""
/routes endpoint.
"""
import marshmallow as mm
from flask import Blueprint
from flask_apispec import doc, marshal_with, use_kwargs

from api.models.db import Route
from api.endpoints.util.auth import common_params, login_required, admin_required

routes = Blueprint('routes', __name__)


class RouteSchema(mm.Schema):
    class Meta:
        strict = True

    city = mm.fields.String(required=True)
    country = mm.fields.String(required=True)


class RoutesSchema(mm.Schema):
    routes = mm.fields.Nested(RouteSchema, many=True)


@routes.route('/api/routes', methods=('POST', ))
@doc(params=common_params)
@use_kwargs(RouteSchema(), locations=('json', ))
@admin_required
def create(**kwargs):
    """Add a new route."""
    route = Route(**kwargs)
    route.save()
    response = {'message': 'Route successfully added.'}
    return response, 201


@routes.route('/api/routes', methods=('GET', ))
@doc(params=common_params)
@marshal_with(RoutesSchema())
@login_required
def get_all():
    """Get all routes."""
    routes = Route.query.all()
    return {'routes': routes}, 200
