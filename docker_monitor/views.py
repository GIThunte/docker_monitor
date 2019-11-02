"""
Routes and views for the flask application.
"""
from datetime import datetime
from flask import render_template, request, json
from docker_monitor import app
from docker_monitor import logic
import docker

docker_api_client = docker.APIClient(base_url='unix://var/run/docker.sock')

@app.route('/')
def index():
    if logic.check_docker_status(docker_api_client):
        id_container_for_inspect = request.args.get('cont_id')
        image_name               = request.args.get('image_name')

        if id_container_for_inspect:
            return render_template('index.html',
                         inspect=json.dumps(logic.docker_inspect(docker_api_client, id_container_for_inspect), indent=4),
                         container_logs=logic.docker_container_logs(docker_api_client, id_container_for_inspect).decode("utf-8"))
                
        elif image_name:
            return render_template('index.html', img_history=logic.get_image_history(docker_api_client, image_name))
            
        return render_template('index.html', container_list=logic.container_list(docker_api_client))
    else:
        return render_template('docker_is_down.html', error='Seems docker is down...')
