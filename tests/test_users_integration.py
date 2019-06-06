import json
import io

from api.models.db import Photo, User
from tests.base import BaseTestCase
from tests.util.factories import PhotoFactory, UserFactory


class UserTestCase(BaseTestCase):
    """Test case for the users blueprint."""

    def test_registration(self):
        """Test user registration works as designed."""
        response = self.register_user()

        result = json.loads(response.data.decode())

        self.assertEqual(result['message'],
                         'You registered successfully. Please log in.')
        self.assertEqual(response.status_code, 201)

    def test_registration_with_invalid_email(self):
        """Test that a user cannot register with an invalid email address."""
        data = {"email": "123456", "password": "Testpassw0rd"}

        res = self.client.post('api/users/register',
                               data=json.dumps(data),
                               headers={'content-type': 'application/json'})

        result = json.loads(res.data.decode())
        self.assertIn('Not a valid email address.',
                      result['messages']['email'])
        self.assertEqual(res.status_code, 422)

    def test_registration_with_invalid_password(self):
        """Test that a user cannot register with an invalid password."""
        data = {"email": "test@example.com", "password": "testpassw0rd"}

        res = self.client.post('api/users/register',
                               data=json.dumps(data),
                               headers={'content-type': 'application/json'})

        result = json.loads(res.data.decode())

        self.assertIn('Your password should contain', result['message'])
        self.assertEqual(res.status_code, 400)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        response = self.register_user()

        self.assertEqual(response.status_code, 201)

        second_response = self.register_user()

        self.assertEqual(second_response.status_code, 409)

        result = json.loads(second_response.data.decode())

        self.assertEqual(result['message'], 'User already exists.')

    def test_user_login(self):
        """Test registered user can login."""
        self.register_user()
        login_response = self.login_user()

        result = json.loads(login_response.data.decode())

        self.assertEqual(result['message'], "You logged in successfully.")
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'Password0'
        }

        response = self.client.post(
            'api/users/login',
            data=json.dumps(not_a_user),
            headers={'content-type': 'application/json'})

        result = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(result['message'],
                         "Invalid email or password. Please try again")

    def test_photo_upload(self):
        """Test user can upload photo."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)

        with self.subTest('Jpgs are uploaded correctly'):
            response = self.client.post(
                '/api/users/photo/upload',
                data={'data': (io.BytesIO(b'yaddayadda'), 'test_photo.jpg')},
                headers={
                    'Authorization': access_token,
                    'content-type': 'multipart/form-data'
                })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(result['message'], 'Photo test_photo.jpg successfully uploaded.')

            with self.app.app_context():
                photo = Photo.query.get(1)
            self.assertEqual(photo.data, b'yaddayadda')

        with self.subTest('None Jpgs are NOT uploaded'):
            response = self.client.post(
                '/api/users/photo/upload',
                data={'data': (io.BytesIO(b'yaddayadda'), 'test_photo.txt')},
                headers={
                    'Authorization': access_token,
                    'content-type': 'multipart/form-data'
                })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 422)
            self.assertEqual(result['messages']['data'], ['Invalid value.'])

    def test_photo_download(self):
        """Test user can download photo."""
        with self.app.app_context():
            photo = PhotoFactory()
            access_token = User.generate_token(photo.uploaded_by_id)

        response = self.client.get(
            '/api/users/photo/download',
            headers={
                'Authorization': access_token,
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, photo.data)
