FROM python:3.9-slim

RUN \
  mkdir /src && \
  cd src && \
  pip install -U pip && \
  pip install \
  django \
  graphene-django \
  graphene-file-upload \
  pillow \
  django-cors-headers \
  django-filter \
  django-graphql-jwt \
  python-decouple \
  psycopg2-binary \
  gunicorn

CMD [ "/bin/bash" ]