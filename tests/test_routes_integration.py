import json

from api.models.db import User
from tests.base import BaseTestCase
from tests.util.factories import RouteFactory, UserFactory


class RouteTestCase(BaseTestCase):
    """Test case for the routes blueprint."""

    def test_create_route(self):
        """Test route can be created."""
        with self.app.app_context():
            user = UserFactory()
            user.is_admin = True
            access_token = User.generate_token(user.id)

            route = RouteFactory.build()

            response = self.client.post('/api/routes',
                                        data=json.dumps({
                                            'city':
                                            route.city,
                                            'country':
                                            route.country,
                                        }),
                                        headers={
                                            'Authorization': access_token,
                                            'content-type': 'application/json'
                                        })

        result = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(result['message'], 'Route successfully added.')

    def test_get_all_routes(self):
        """Test can get all routes."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)
            route_1 = RouteFactory()
            route_2 = RouteFactory()

            response = self.client.get('/api/routes',
                                       headers={
                                           'Authorization': access_token,
                                           'content-type': 'application/json'
                                       })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result['routes']), 2)
            self.assertEqual(result['routes'][0]['city'], route_1.city)
            self.assertEqual(result['routes'][0]['country'], route_1.country)
            self.assertEqual(result['routes'][1]['city'], route_2.city)
            self.assertEqual(result['routes'][1]['country'], route_2.country)
