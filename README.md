know-sql
========

HTTP frontend to [Postgresql](http://www.postgresql.org/).  URLs are
turned into postgres function calls that accept and return JSON.  HTTP
status codes can be RAISEd from plpgsql functions.

usage
=====

Clone and run setup.py, or install the package:

  pip install know-sql

The server can be run now:

  know-sql <args...>

The module can also be run directly:

  python -m ksql

it can be used with gunicorn, uwsgi, or any other wsgi server by
importing 'ksql.app'.