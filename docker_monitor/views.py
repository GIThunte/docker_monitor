"""
Routes and views for the flask application.
"""
from datetime import datetime
from flask import render_template, request, json
from docker_monitor import app
from docker_monitor import logic
import docker

docker_sdk_client = docker.from_env()
docker_client_api = docker.APIClient(base_url='unix://var/run/docker.sock')

@app.route('/')
def index():
    id_container_for_inspect = request.args.get('cont_id')

    if id_container_for_inspect:
        return render_template('index.html',
                     inspect=json.dumps(logic.docker_inspect(docker_client_api, id_container_for_inspect), indent=4),
                     container_logs=logic.docker_container_logs(docker_sdk_client, id_container_for_inspect).decode("utf-8"))
            
    return render_template('index.html', container_list=logic.container_list(docker_sdk_client))
