FROM continuumio/miniconda3:latest
LABEL maintainer="musonyengigi@gmail.com"
LABEL description="Ticket booking and flights reservation micro api."

COPY . /flights
WORKDIR /flights/

RUN apt-get update && apt-get -y install build-essential python3-dev libpq-dev postgresql-client

RUN pip install --upgrade-strategy only-if-needed --no-cache-dir -q \
        -r requirements.txt

ENV PYTHONPATH $PYTHONPATH:/flights/

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "--timeout", "350", "api.unicorn:app"]
