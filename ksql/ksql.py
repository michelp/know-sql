import os, re

from json import dumps
import logging
import psycopg2
from psycopg2 import connect
from psycopg2.extras import Json
from werkzeug.wrappers import (
    Request,
    Response,
)
from werkzeug.exceptions import (
    default_exceptions,
    InternalServerError,
    Unauthorized,
    NotFound,
)

logging.basicConfig()
logger = logging.getLogger(__name__)

location_re = re.compile(
    r"/(?P<db>\w+)/(?P<schema>\w+)/(?P<function>\w+)(?P<path>/.*){0,}$"
    )


def login_required(realm='login required'):
    return Response(
        'Login Required', 401,
        {'WWW-Authenticate': 'Basic realm="%s"' % realm}
    )

def not_found(realm='login required'):
    return Response(
        'Login Required', 401,
        {'WWW-Authenticate': 'Basic realm="%s"' % realm}
    )


@Request.application
def app(request):
    match = location_re.match(request.path)
    if not match:
        raise NotFound

    groups = match.groups()
    if not groups:
        raise NotFound

    auth = request.authorization
    if not auth:
        return login_required()

    db, schema, func_name, path = groups
    path = '' if path is None else path
    username = auth.username
    password = auth.password

    environ = Json({k: v for k, v in request.environ.items() if k.isupper()})
    path = Json(filter(None, path.split('/')))
    args = Json(dict(request.args))
    try:
        db = connect(database=db, user=username, password=password)
    except Exception:
        raise InternalServerError
    with db as conn:
        with conn.cursor() as cur:
            try:
                cur.callproc(
                    'http.process_request',
                    (request.method,
                     schema, func_name,
                     environ, path, args,
                     request.get_data()))
                result = cur.fetchone()[0]
                response = Response(dumps(result), mimetype='application/json')
                conn.commit()
                return response
            except psycopg2.Error as e:
                conn.rollback()
                logger.exception(request.path)
                if e.diag.message_primary.isdigit():
                    code = int(e.diag.message_primary)
                    raise default_exceptions.get(code, InternalServerError)
                else:
                    raise InternalServerError(e.diag.message_primary)
            except Exception:
                conn.rollback()
                logger.exception(request.path)
                raise InternalServerError
