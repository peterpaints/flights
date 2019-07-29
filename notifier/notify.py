import datetime

from celery import Celery
from celery.schedules import crontab
from flask_mail import Mail, Message
from sqlalchemy import and_

from api import app
from api.models.db import Flight

mail_app = app.create_app()
mail = Mail(mail_app)

celery_settings = {
    'broker_url': 'redis://redis:6379/0',
    'result_backend': 'redis://redis:6379/0',
}
celery = Celery('notifier', broker=celery_settings['broker_url'])
celery.conf.update(celery_settings)
celery.conf.beat_schedule = {
    'notify_users': {
        'task': 'notify.notify_users',
        'schedule': crontab(hour=0, minute=0)
    }
}


@celery.task
def notify_users():
    with mail_app.app_context():
        from_date = datetime.datetime.today() + datetime.timedelta(days=1)
        to_date = from_date + datetime.timedelta(days=1)
        flights = Flight.query.filter(
            and_(Flight.departure >= from_date,
                 Flight.departure <= to_date)).all()

        tickets = [flight.tickets.all() for flight in flights]

        users = []
        for flight in tickets:
            for ticket in flight:
                users.append((ticket.flight, ticket.booked_by))

        for flight, user in users:
            date = flight.departure.strftime('%d %b, %Y')
            time = flight.departure.strftime('%I.%M %p')
            msg = Message(subject='Hello',
                          sender=mail_app.config.get('MAIL_USERNAME'),
                          recipients=[user.email],
                          body=f'Hi! Your flight to {flight.destination.city} on '
                               f'{date} at '
                               f'{time} is almost here!')
            mail.send(msg)
