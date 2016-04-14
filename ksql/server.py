import os
import re
from json import dumps
import logging
import psycopg2
from psycopg2.extras import Json
from werkzeug.wrappers import Request, Response

global conn
conn = psycopg2.connect('postgresql://michel@/michel')
logging.basicConfig()
logger = logging.getLogger(__name__)

location_re = re.compile(
    r"/(?P<db>\w+)/(?P<schema>\w+)/(?P<function>\w+)(?P<path>/.*){0,}$"
    )

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
    except:
        logger.exception(request.path)
        conn.rollback()
        
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 4000, app, use_debugger=True)
