"""
A script for seeding the database
To run, call the script along with the desired arguments:
```sh
> docker compose run flights python api/models/seed.py --email bla@bla.com --password Password1 --admin True
```
"""
import argparse
import factory

from api import app
from tests.util.factories import FlightFactory, RouteFactory, UserFactory


def seed_routes():
    for i in range(100):
        RouteFactory()


def seed_flights():
    for i in range(5):
        FlightFactory()


def seed_user(args):
    UserFactory(email=args.email, password=args.password, is_admin=args.admin)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e',
                        '--email',
                        required=False,
                        type=str,
                        default=factory.Faker('email'),
                        help='User email')

    parser.add_argument('-p',
                        '--password',
                        required=False,
                        type=str,
                        default=factory.Faker('password',
                                              length=10,
                                              special_chars=True,
                                              digits=True,
                                              upper_case=True,
                                              lower_case=True),
                        help='User password')

    parser.add_argument('-a',
                        '--admin',
                        required=False,
                        type=bool,
                        default=factory.Faker('boolean',
                                              chance_of_getting_true=0),
                        help='Create user as admin')

    args = parser.parse_args()
    flights_app = app.create_app()
    with flights_app.app_context():
        seed_routes()
        seed_flights()
        seed_user(args)


if __name__ == '__main__':
    main()
