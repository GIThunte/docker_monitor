"""
Routes and views for the flask application.
"""
from datetime import datetime
from flask import render_template, request, json
from docker_monitor import app
from docker_monitor import logic
import docker

host_lists = {'localhost': 'tcp://10.1.0.65:3325', 'localhost-test': 'tcp://0.0.0.0:3322'}

@app.route('/')
def dashboard():

    host_addr = request.args.get('host_addr')

    if host_addr:
        return redirect(url_for('index', host_addr=host_addr))

    return render_template('dashboard.html', list_of_hosts=[logic.get_status_hosts(x, host_lists[x]) for x in host_lists])

@app.route('/monitor')
def index():
    
    host_addr = request.args.get('host_addr')
    docker_api_client = docker.APIClient(base_url=host_addr)

    if logic.check_docker_status(docker_api_client, host_addr):

        id_container_for_inspect = request.args.get('cont_id')
        image_name               = request.args.get('image_name')

        if id_container_for_inspect:
            return render_template('index.html',
                         inspect=json.dumps(logic.docker_inspect(docker_api_client, id_container_for_inspect), indent=4),
                         container_logs=logic.docker_container_logs(docker_api_client, id_container_for_inspect).decode("utf-8"),
                         host_addr=host_addr)
                
        elif image_name:
            return render_template('index.html', img_history=logic.get_image_history(docker_api_client, image_name), host_addr=host_addr)
            
        return render_template('index.html', container_list=logic.container_list(docker_api_client), host_addr=host_addr)
    else:
        return render_template('docker_is_down.html', error='Seems docker is down... HOST: {}'.format(host_addr))

