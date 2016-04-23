import base64
from json import loads
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.datastructures import Headers
from ksql import app


def auth_headers(user, password):
    h = Headers()
    h.add('Authorization', 'Basic ' + base64.b64encode('%s:%s' % (user, password)))
    return h


def test_get():
    c = Client(app, BaseResponse)
    resp = c.get('/michel/http/test/a/b/c?x=3&x=4&y=z', headers=auth_headers('michel', 'michel'))
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'application/json'
    assert loads(resp.data) ==  [
        {u'path': ['a', 'b', 'c'],
         u'args': {u'x': [u'3', u'4'], u'y': [u'z']},
         u'environ':
         {u'CONTENT_LENGTH': u'0',
          u'HTTP_AUTHORIZATION':
          u'Basic bWljaGVsOm1pY2hlbA==',
          u'CONTENT_TYPE': u'',
          u'SERVER_NAME': u'localhost',
          u'SCRIPT_NAME': u'',
          u'REQUEST_METHOD': u'GET',
          u'HTTP_HOST': u'localhost',
          u'PATH_INFO': u'/michel/http/test/a/b/c',
          u'SERVER_PORT': u'80',
          u'SERVER_PROTOCOL': u'HTTP/1.1',
          u'QUERY_STRING': u'x=3&x=4&y=z'}}
    ]

def test_post():
    c = Client(app, BaseResponse)
    resp = c.post(
        '/michel/http/test/a/b/c?x=3&x=4&y=z',
        headers=auth_headers('michel', 'michel'),
        data='{"yo": "dog"}')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'application/json'
    data = loads(resp.data)[0]

    assert data['path'] == [u'a', u'b', u'c']
    assert data['request'] == {u'yo': u'dog'}
    assert data['args'] == {u'x': [u'3', u'4'], u'y': [u'z']}
    assert data['environ'] == {
        u'HTTP_CONTENT_LENGTH': u'13',
        u'CONTENT_LENGTH': u'13',
        u'HTTP_AUTHORIZATION':
        u'Basic bWljaGVsOm1pY2hlbA==',
        u'CONTENT_TYPE': u'',
        u'SERVER_NAME': u'localhost',
        u'SCRIPT_NAME': u'',
        u'REQUEST_METHOD': u'POST',
        u'HTTP_HOST': u'localhost',
        u'PATH_INFO': u'/michel/http/test/a/b/c',
        u'SERVER_PORT': u'80',
        u'SERVER_PROTOCOL': u'HTTP/1.1',
        u'QUERY_STRING': u'x=3&x=4&y=z'
    }

def test_get_not_found():
    c = Client(app, BaseResponse)
    resp = c.get(
        '/michel/http/test_not_found',
        headers=auth_headers('michel', 'michel')
    )
    assert resp.status_code == 404
