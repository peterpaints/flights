import json
import unittest

from api import app
from api.models.db import db
from tests import settings


class BaseTestCase(unittest.TestCase):
    """Define a base testcase, with a reusable setup."""

    user_data = {"email": "johndoe@test.com", "password": "Testpassw0rd"}

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app.create_app(config_obj=settings, TESTING=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self):
        """Register a test user."""
        return self.client.post('api/users/register',
                                data=json.dumps(self.user_data),
                                headers={'content-type': 'application/json'})

    def login_user(self, user=user_data):
        """Log in a test user."""
        return self.client.post('api/users/login',
                                data=json.dumps(user),
                                headers={'content-type': 'application/json'})

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
