import json

from api.models.db import User
from tests.base import BaseTestCase
from tests.util.factories import FlightFactory, TicketFactory, UserFactory


class TicketTestCase(BaseTestCase):
    """Test case for the tickets blueprint."""

    def test_create_ticket(self):
        """Test ticket can be created."""
        with self.app.app_context():
            user = UserFactory()
            user.is_admin = True
            access_token = User.generate_token(user.id)

            flight = FlightFactory()

            response = self.client.post('/api/tickets/book',
                                        data=json.dumps(
                                            {'flight_id': flight.id}),
                                        headers={
                                            'Authorization': access_token,
                                            'content-type': 'application/json'
                                        })

        result = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(result['message'], 'Ticket successfully booked.')

    def test_get_by_user_id(self):
        """Test can get ticket by user id."""
        with self.app.app_context():
            user = UserFactory()
            user.is_admin = True
            access_token = User.generate_token(user.id)
            ticket = TicketFactory()

            response = self.client.get(f'/api/tickets/{ticket.booked_by_id}',
                                       headers={
                                           'Authorization': access_token,
                                           'content-type': 'application/json'
                                       })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result['tickets']), 1)
            self.assertEqual(result['tickets'][0]['flight_id'], ticket.flight_id)

    def test_get_mine(self):
        """Test user can get own ticket details."""
        with self.app.app_context():
            user = UserFactory()
            access_token = User.generate_token(user.id)
            ticket = TicketFactory.build()
            ticket.booked_by = user
            ticket.save()

            response = self.client.get('/api/tickets/mine',
                                       headers={
                                           'Authorization': access_token,
                                           'content-type': 'application/json'
                                       })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result['tickets']), 1)
            self.assertEqual(result['tickets'][0]['flight_id'], ticket.flight_id)

    def test_ticket_cancel(self):
        """Test can cancel ticket."""
        with self.app.app_context():
            user = UserFactory()
            user.is_admin = True
            access_token = User.generate_token(user.id)
            ticket = TicketFactory.build()
            ticket.booked_by = user
            ticket.save()

            response = self.client.delete(f'/api/tickets/cancel/{ticket.id}',
                                          headers={
                                              'Authorization': access_token,
                                              'content-type': 'application/json'
                                          })

            result = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(result['message'], 'Ticket successfully cancelled.')

            with self.subTest('Ticket no longer exists'):
                response = self.client.get(f'/api/tickets/{user.id}',
                                           headers={
                                               'Authorization': access_token,
                                               'content-type': 'application/json'
                                           })

                result = json.loads(response.data.decode())
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(result['tickets']), 0)
