FROM continuumio/miniconda3:latest
LABEL maintainer="musonyengigi@gmail.com"
LABEL description="Ticket booking and flights reservation micro api."

COPY . /flights
WORKDIR /flights/

RUN apt-get update && apt-get -y install \
    build-essential \
    python3-dev \
    libpq-dev \
    postgresql-client \
    netcat

RUN pip install --upgrade-strategy only-if-needed --no-cache-dir -q \
        -r requirements.txt

RUN ["chmod", "+x", "bin/startup.sh", "bin/wait_for_it.sh"]

ENV PYTHONPATH $PYTHONPATH:/flights/

CMD ["bin/startup.sh"]
