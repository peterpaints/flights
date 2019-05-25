FROM continuumio/miniconda:latest
LABEL maintainer="musonyengigi@gmail.com"
LABEL description="Exposes recipe search models via a Python2 Flask-based web service."

ADD devops/python/* /home/docker/

RUN pip install --upgrade-strategy only-if-needed --no-cache-dir -q \
        -r requirements.txt

ADD . /tajine
ENV PYTHONPATH $PYTHONPATH:/tajine/
WORKDIR /tajine/

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:6100", "--timeout", "350", "--access-logformat", "%(h)s %(l)s %(t)s \"%(r)s\" %(s)s %(b)sB %(L)ss \"%(a)s\"", "--access-logfile", "-", "tajine.unicorn:app"]
