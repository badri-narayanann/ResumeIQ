from backend import create_app
from wsgiref.simple_server import make_server
import os

if __name__ == '__main__':
    app = create_app()
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5001'))
    print(f"Serving on http://{host}:{port}")
    with make_server(host, port, app) as httpd:
        httpd.serve_forever()
