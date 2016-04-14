"""Know-SQL

A simple json API proxy over HTTP to Postgres.

Usage:
  ksql.py

Options:
  -h --help     Show this screen.
  -d --database Database connection string.

"""

import os
import re
from json import dumps
import logging
import psycopg2
from psycopg2.extras import Json
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import default_exceptions, InternalServerError

global conn
conn = psycopg2.connect('postgresql://michel@/michel')
logging.basicConfig()
logger = logging.getLogger(__name__)

location_re = re.compile(
    r"/(?P<db>\w+)/(?P<schema>\w+)/(?P<function>\w+)(?P<path>/.*){0,}$"
    )

def make_app(dsn):
    @Request.application 
    def app(request): 
        conn.rollback() 
        try:
            groups = location_re.match(request.path).groups()
            if not groups:
                raise Exception('badz')
            db, schema, func_name, path = groups
            path = '' if path is None else path

            environ = Json({k: v for k, v in request.environ.items() if k.isupper()})
            path = Json(filter(None, path.split('/')))
            args = Json(dict(request.args))

            method = request.method
            proc_args = (schema, func_name)
            if method == 'GET':
                proc_args = proc_args + (environ, path, args)
            elif method == 'POST':
                proc_args = proc_args + (environ, path, args, request.get_data())
            with conn.cursor() as cur:
                cur.callproc('http.get', proc_args)
                conn.commit()
                result = cur.fetchone()[0]
                response = Response(dumps(result), mimetype='application/json')
                response.cache_control.max_age = 300
                return response
        except psycopg2.Error, e:
            try:
                conn.rollback()
                logger.exception(request.path)
                code = int(e.diag.message_primary)
            except Exception:
                raise InternalServerError
            raise default_exceptions.get(code, InternalServerError)
    return app
        
if __name__ == '__main__':
    from docopt import docopt
    from werkzeug.serving import run_simple
    arguments = docopt(__doc__, version='Know-SQL 0.1')
    import pdb; pdb.set_trace
    bind = arguments.get('--bind', '0.0.0.0')
    port = arguments.get('--port', 4000)
    dsn = arguments.get('--database', '')
    run_simple(bind, port, make_app(dsn), use_debugger=True)
