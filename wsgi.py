"""
WSGI Application entrypoint for PythonAnywhere / Gunicorn.

Serves the static site plus the account API (sign-up, sign-in, synced preferences) so accounts
work here exactly as they do under server.py.
"""
import json
import os
import sys
import mimetypes

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

import accounts  # noqa: E402  (needs ROOT_DIR on sys.path first)


class _Headers:
    """Case-insensitive header lookup over a WSGI environ."""

    def __init__(self, environ):
        self.environ = environ

    def get(self, name, default=None):
        key = name.upper().replace('-', '_')
        if key == '_HTTPS':
            return self.environ.get('wsgi.url_scheme') == 'https' or None
        if key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            return self.environ.get(key, default)
        return self.environ.get('HTTP_' + key, default)


def _account_api(environ, start_response, path):
    headers = _Headers(environ)

    def read_body(limit):
        length = int(environ.get('CONTENT_LENGTH') or 0)
        if length > limit:
            raise accounts.AuthError('Request is too large.', 413)
        return environ['wsgi.input'].read(length) if length else b''

    client_ip = (headers.get('X-Forwarded-For') or '').split(',')[0].strip() or environ.get('REMOTE_ADDR', '')
    status, payload, cookie = accounts.handle_request(environ.get('REQUEST_METHOD', 'GET'), path, headers, read_body, client_ip)
    body = json.dumps(payload).encode('utf-8')
    response_headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
        ('Content-Length', str(len(body))),
        ('Cache-Control', 'no-store'),
    ]
    if cookie:
        response_headers.append(('Set-Cookie', cookie))
    reason = {200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found',
              405: 'Method Not Allowed', 409: 'Conflict', 413: 'Payload Too Large',
              429: 'Too Many Requests', 500: 'Internal Server Error', 503: 'Service Unavailable'}.get(status, 'OK')
    start_response(f'{status} {reason}', response_headers)
    return [body]


def _not_found(start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'404 Not Found']


def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')

    if accounts.is_api_path(path):
        return _account_api(environ, start_response, path)

    if accounts.is_private_path(path):
        return _not_found(start_response)

    if path == '/' or path == '':
        file_path = os.path.join(ROOT_DIR, 'index.html')
    else:
        file_path = os.path.realpath(os.path.join(ROOT_DIR, path.lstrip('/')))
        # Never serve anything outside the site folder (e.g. /../../etc/passwd).
        if not file_path.startswith(ROOT_DIR + os.sep):
            return _not_found(start_response)

    if os.path.isfile(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'
        with open(file_path, 'rb') as f:
            content = f.read()
        start_response('200 OK', [
            ('Content-Type', mime_type),
            ('Content-Length', str(len(content))),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [content]

    return _not_found(start_response)


app = application
