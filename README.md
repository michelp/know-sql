know-sql
========

HTTP frontend to [Postgresql](http://www.postgresql.org/).  json in, json out.

server
======

server.py implements the HTTP frontent, but it could be implemented in
just about any language.  Fork it!!


usage
=====

Install the package:

  pip install know-sql

The server can be run directly from python:

  python -m ksql

The module can also be used with gunicorn, uwsgi, or any other wsgi server.