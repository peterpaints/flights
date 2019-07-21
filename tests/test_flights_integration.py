import json
from datetime import datetime, timedelta

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

    def test_get_all_flights(self):
        """Test can get all flights."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)
            flight_1 = FlightFactory()
            flight_2 = FlightFactory()

            response = self.client.get('/api/flights',
                                       headers={
                                           'Authorization': access_token,
                                           'content-type': 'application/json'
                                       })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result['flights']), 2)
            self.assertEqual(result['flights'][0]['origin_id'], flight_1.origin_id)
            self.assertEqual(result['flights'][0]['destination_id'], flight_1.destination_id)
            self.assertEqual(result['flights'][1]['origin_id'], flight_2.origin_id)
            self.assertEqual(result['flights'][1]['destination_id'], flight_2.destination_id)

    def test_get_all_flights_with_date_range(self):
        """Test can get all flights filtered by date range."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)
            flight_1 = FlightFactory()

            with self.subTest('Raise an error for dates with wrong format'):
                response = self.client.get('/api/flights',
                                           query_string={
                                               'from': 'not-a-real-date',
                                               'to': 'also-not-real'
                                           },
                                           headers={
                                               'Authorization': access_token,
                                               'content-type': 'application/json'
                                           })

                result = json.loads(response.data.decode())
                self.assertEqual(response.status_code, 422)
                self.assertIn("does not match format '%Y-%m-%dT%H:%M:%S'", result['messages'])

            with self.subTest('No results for flights in the past'):
                response = self.client.get('/api/flights',
                                           query_string={
                                               'from': '2018-07-19T00:00:00',
                                               'to': '2018-07-23T00:00:00'
                                           },
                                           headers={
                                               'Authorization': access_token,
                                               'content-type': 'application/json'
                                           })

                result = json.loads(response.data.decode())
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(result['flights']), 0)

            with self.subTest('Results adhere to date range filter'):
                from_date = flight_1.departure - timedelta(days=1)
                to_date = flight_1.arrival + timedelta(days=1)

                response = self.client.get('/api/flights',
                                           query_string={
                                               'from': from_date.strftime('%Y-%m-%dT%H:%M:%S'),
                                               'to': to_date.strftime('%Y-%m-%dT%H:%M:%S')
                                           },
                                           headers={
                                               'Authorization': access_token,
                                               'content-type': 'application/json'
                                           })

                result = json.loads(response.data.decode())
                self.assertEqual(response.status_code, 200)
                self.assertGreater(len(result['flights']), 0)

    def test_get_by_route(self):
        """Test can get flight by route taken."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)
            flight = FlightFactory()

            response = self.client.get('/api/flights/route',
                                       query_string={
                                           'origin': flight.origin_id,
                                           'destination': flight.destination_id
                                       },
                                       headers={
                                           'Authorization': access_token,
                                           'content-type': 'application/json'
                                       })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result['flights']), 1)
            self.assertEqual(result['flights'][0]['origin_id'], flight.origin_id)
            self.assertEqual(result['flights'][0]['destination_id'], flight.destination_id)

    def test_get_by_origin(self):
        """Test can get flight by origin."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)
            flight = FlightFactory()

            response = self.client.get(f'/api/flights/origin/{flight.origin_id}',
                                       headers={
                                           'Authorization': access_token,
                                           'content-type': 'application/json'
                                       })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result['flights']), 1)
            self.assertEqual(result['flights'][0]['origin_id'], flight.origin_id)
            self.assertEqual(result['flights'][0]['destination_id'], flight.destination_id)

    def test_get_by_destination(self):
        """Test can get flight by destination."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)
            flight = FlightFactory()

            response = self.client.get(f'/api/flights/destination/{flight.destination_id}',
                                       headers={
                                           'Authorization': access_token,
                                           'content-type': 'application/json'
                                       })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result['flights']), 1)
            self.assertEqual(result['flights'][0]['origin_id'], flight.origin_id)
            self.assertEqual(result['flights'][0]['destination_id'], flight.destination_id)
