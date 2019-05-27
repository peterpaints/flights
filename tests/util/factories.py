import factory

from api.models.db import db, Flight, Route, User


class ModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factories for SQLAlchemy ORM models"""

    class Meta:
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


class UserFactory(ModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    password = factory.Faker('password',
                             length=10,
                             special_chars=True,
                             digits=True,
                             upper_case=True,
                             lower_case=True)
    is_admin = factory.Faker('boolean', chance_of_getting_true=0)


class RouteFactory(ModelFactory):
    class Meta:
        model = Route

    city = factory.Faker('city')
    country = factory.Faker('country')


class FlightFactory(ModelFactory):
    class Meta:
        model = Flight

    capacity = factory.Faker('pyint', min=0, max=999, step=1)
    origin = factory.LazyAttribute(lambda a: RouteFactory().id)
    destination = factory.LazyAttribute(lambda a: RouteFactory().id)
    departure = factory.Faker('future_datetime',
                              end_date='+1d',
                              tzinfo=None)
    arrival = factory.Faker('date_time_between',
                            start_date='+1d',
                            end_date='+7d',
                            tzinfo=None)
    price = factory.Faker('pyfloat',
                          left_digits=2,
                          right_digits=2,
                          positive=True)
