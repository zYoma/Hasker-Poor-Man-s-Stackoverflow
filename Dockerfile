FROM python:3.8.5

ENV PYTHONUNBUFFERED 1
ENV POETRY_HOME /opt/poetry
ENV PATH $POETRY_HOME/bin:$PATH
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VERSION=1.2.2

COPY poetry.lock pyproject.toml ./

RUN apt -y update \
    && apt -y install \
       gcc \
    && pip install --upgrade pip \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install

ADD ./src /app
WORKDIR /app
