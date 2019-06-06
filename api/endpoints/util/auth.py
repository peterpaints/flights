from functools import wraps

from flask import abort, request

from api.models.db import User


common_params = {
    'Authorization': {
        'description': 'JWT token',
        'in': 'header',
        'type': 'string',
        'required': True
    }
}


def login_required(func):
    """Ensure a function can only be executed if there is a token."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token:
            user_id = User.decode_token(access_token)
            if isinstance(user_id, str):
                abort(404, user_id)
            request.user_id = user_id
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    """With great power comes great responsibility."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token:
            user_id = User.decode_token(access_token)
            user = User.query.get(user_id)
            if not user.is_admin:
                abort(401, 'You\'re not authorized to perform this action.')
            request.user_id = user_id
        return func(*args, **kwargs)
    return wrapper
