"""
/users endpoint.

"""
from io import BytesIO

import marshmallow as mm
import sqlalchemy
from flask import Blueprint, request, send_file
from flask_apispec import doc, use_kwargs

from api.models.db import User, Photo
from api.endpoints.util.auth import common_params, login_required

users = Blueprint('users', __name__)


class UserRegistrationSchema(mm.Schema):

    class Meta:
        strict = True

    email = mm.fields.Email(required=True)
    password = mm.fields.String(required=True,
                                validate=[mm.validate.Length(min=6, max=36)])


class UserPhotoSchema(mm.Schema):

    class Meta:
        strict = True

    data = mm.fields.Field(
        validate=lambda f: f.mimetype in ["image/jpeg", "image/png"],
        required=True)


@users.route('/api/users/register', methods=('POST', ))
@use_kwargs(UserRegistrationSchema(), locations=('json', ))
def register(email, password):
    """Handle POST request at /users/register."""
    try:
        user = User(email=email, password=password)
        user.save()

        response = {'message': 'You registered successfully. Please log in.'}
        return response, 201

    except sqlalchemy.exc.IntegrityError:
        response = {'message': 'User already exists.'}
        return response, 409

    except AssertionError as e:
        response = {'message': str(e)}
        return response, 401


@users.route('/api/users/login', methods=('POST', ))
@use_kwargs(UserRegistrationSchema(), locations=('json', ))
def login(email, password):
    """Handle POST request at /users/login."""
    try:
        # Get the user object using their email (unique to every user)
        user = User.query.filter_by(email=email).first()

        # Try to authenticate the found user using their password
        if user and user.is_registered_password(password):
            # Generate the access token.
            access_token = user.generate_token(user.id)
            if access_token:
                response = {
                    'message': 'You logged in successfully.',
                    'access_token': access_token.decode()
                }
                return response, 200
        else:
            # User does not exist. Therefore, we return an error message
            response = {
                'message': 'Invalid email or password. Please try again'
            }
            return response, 401

    except Exception as e:
        response = {'message': str(e)}

        return response, 500


@users.route('/api/users/photo/upload', methods=('POST', ))
@doc(params=common_params)
@use_kwargs(UserPhotoSchema(), locations=('files', ))
@login_required
def upload(data):
    try:
        photo = Photo(name=data.filename,
                      data=data.read(),
                      uploaded_by=request.user_id)
        photo.save()
        response = {'message': f'Photo {photo.name} successfully uploaded.'}
        return response, 201
    except Exception as e:
        response = {'message': str(e)}

        return response, 500


@users.route('/api/users/photo/download', methods=('GET', ))
@doc(params=common_params)
@login_required
def download():
    try:
        photo = Photo.query.filter_by(uploaded_by=request.user_id).order_by(
            Photo.created_at.desc()).first()
        return send_file(BytesIO(photo.data),
                         attachment_filename=photo.name,
                         as_attachment=True)
    except Exception as e:
        response = {'message': str(e)}

        return response, 500
