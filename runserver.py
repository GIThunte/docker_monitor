#!env/bin/python3

from os import environ
from docker_monitor import app
from gevent.pywsgi import WSGIServer

if __name__ == '__main__':
    app_host = environ.get('SERVER_HOST', '0.0.0.0')
    app_port = int(environ.get('SERVER_PORT', '5355'))
    app_env  = environ.get('SERVER_ENV', 'dev') # prod

    if 'prod' in app_env:         
        http_server = WSGIServer((app_host, int(app_port)), app)
        http_server.serve_forever()
    elif 'dev' in app_env:
        app.run(app_host, app_port)
