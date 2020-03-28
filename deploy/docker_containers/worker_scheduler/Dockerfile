FROM python:3.8

WORKDIR /app/src

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

ENV PATH="/root/.poetry/bin:${PATH}"

CMD poetry run gunicorn project.wsgi
