"""
WSGI Application entrypoint for PythonAnywhere / Gunicorn.
"""
import os
import sys
import mimetypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    if path == '/' or path == '':
        file_path = os.path.join(root_dir, 'index.html')
    else:
        file_path = os.path.join(root_dir, path.lstrip('/'))
        
    if os.path.exists(file_path) and os.path.isfile(file_path):
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
        
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'404 Not Found']

app = application
