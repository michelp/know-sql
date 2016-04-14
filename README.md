know-sql
========

HTTP frontend to [Postgresql](http://www.postgresql.org/).  json in, json out.

server
======

server.py implements the HTTP frontent, but it could be implemented in
just about any language.  Fork it!!


usage
=====

The server can be run directly from python:

  python server.py 'postgres@dbhost...'

The module can also be used with gunicorn, uwsgi, or any other wsgi server.