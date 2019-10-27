#!/usr/bin/env python3
import docker
import argparse
import json
from flask import Flask
from flask import *

app               = Flask(__name__)
docker_client     = docker.from_env()
docker_client_new = docker.APIClient(base_url='unix://var/run/docker.sock')

def docker_inspect(client_obj, container_id):
    return(client_obj.inspect_container(container_id))

def get_containers(connect_obj):
    return(connect_obj.containers.list(all=True))

def container_list(connect_obj):
    return([{'name': x.name, 'id': x.short_id, 'status': x.status } for x in get_containers(connect_obj)])

@app.route('/')
def index():
    id_container_for_inspect = request.args.get('cont_id')

    if id_container_for_inspect:
        return render_template('index.html', inspect=json.dumps(docker_inspect(docker_client_new, id_container_for_inspect), indent=4))
            
    return render_template('index.html', container_list=container_list(docker_client))

if __name__ == '__main__':
   app.run(host='0.0.0.0')
