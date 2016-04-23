import os, re

from json import loads, dumps
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

MAX_CONTENT_LENGTH = (1024 * 1024) # 1MB

location_re = re.compile(
    r"/(?P<db>\w+)/(?P<schema>\w+)/(?P<function>\w+)(?P<path>/.*){0,}$"
    )


def login_required(realm='login required'):
    return Response(
        'Login Required', 401,
        {'WWW-Authenticate': 'Basic realm="%s"' % realm}
    )


@Request.application
def app(request):
    request.max_content_length = MAX_CONTENT_LENGTH

    auth = request.authorization
    if not auth:
        return login_required()

    match = location_re.match(request.path)

    if not match:
        return NotFound()

    groups = match.groups()
    if not groups:
        return NotFound()

    db, schema, func_name, path = groups
    path = '' if path is None else path
    username = auth.username
    password = auth.password

    try:
        environ = Json({k: v for k, v in request.environ.items() if k.isupper()})
        path = Json(filter(None, path.split('/')))
        args = Json(dict(request.args))
        data = Json(loads(request.get_data() or 'null'))
        db = connect(database=db, user=username, password=password)
    except Exception:
        logger.exception(request.path)
        return InternalServerError()
    with db.cursor() as cur:
        try:
            cur.callproc(
                'http.process_request',
                (request.method,
                 schema, func_name,
                 environ, path, args,
                 data))
            result = cur.fetchone()[0]
            response = Response(dumps(result), mimetype='application/json')
            db.commit()
            return response
        except psycopg2.Error as e:
            db.rollback()
            logger.exception(request.path)
            if e.diag.message_primary.isdigit():
                code = int(e.diag.message_primary)
                return default_exceptions.get(code, InternalServerError)()
            else:
                return InternalServerError(e.diag.message_primary)
        except Exception:
            db.rollback()
            logger.exception(request.path)
            return InternalServerError
