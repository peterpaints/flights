import json

from api.models.db import User
from tests.base import BaseTestCase
from tests.util.factories import FlightFactory, RouteFactory, UserFactory
from tests.util.helpers import JsonEncoderWithDatetime


class FlightTestCase(BaseTestCase):
    """Test case for the flights blueprint."""

    def test_create_flight(self):
        """Test flight can be created."""
        with self.app.app_context():
            user = UserFactory()
            user.is_admin = True
            access_token = User.generate_token(user.id)

            route_1 = RouteFactory()
            route_2 = RouteFactory()
            flight = FlightFactory.build()

            response = self.client.post('/api/flights',
                                        data=json.dumps(
                                            {
                                                'origin_id': route_1.id,
                                                'destination_id': route_2.id,
                                                'departure': flight.departure,
                                                'arrival': flight.arrival,
                                                'price': flight.price,
                                                'capacity': flight.capacity
                                            },
                                            cls=JsonEncoderWithDatetime),
                                        headers={
                                            'Authorization': access_token,
                                            'content-type': 'application/json'
                                        })

        result = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(result['message'], 'Flight created.')

    # def test_get_by_route(self):
    #     """Test can get flight by route taken."""
    #     with self.app.app_context():
    #         user = UserFactory()
    #         access_token = User.generate_token(user.id)
    #         flight = FlightFactory()

    #         response = self.client.get('/api/flights/route',
    # )
