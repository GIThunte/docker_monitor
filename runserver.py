#!env/bin/python3

"""
This script runs the docker_monitor application using a development server.
"""
from os import environ
from docker_monitor import app

if __name__ == '__main__':
    app_host = environ.get('SERVER_HOST', '0.0.0.0')
    app_port = int(environ.get('SERVER_PORT', '5355'))
 
    app.run(app_host, app_port)
