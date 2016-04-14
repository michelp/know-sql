know-sql
========

HTTP frontend to [Postgresql](http://www.postgresql.org/).  URLs are
turned into postgres function calls that accept and return JSON.  HTTP
status codes can be RAISEd from plpgsql functions.

server
======

ksql/ksql.py implements the HTTP frontent in Python, but it could be
implemented in just about any language that can interface postgres.
Fork it!!

usage
=====

Clone and run setup.py, or install the package:

  pip install know-sql

The server can be run now:

  know-sql <args...>

The module can also be run directly:

  python -m ksql

it can also be used with gunicorn, uwsgi, or any other wsgi server.