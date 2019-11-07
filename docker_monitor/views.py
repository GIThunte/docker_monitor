"""
Routes and views for the flask application.
"""
from datetime import datetime
from flask import render_template, request, json
from docker_monitor import app
from docker_monitor import logic
from jinja2 import Template
import docker
import json

ip      = '10.1.0.65'
port    = 27017
db      = 'host_lists'
coll    = 'hosts'

@app.route('/add_new_host', methods=['GET', 'POST'])
def add_new_host():
    if request.method == 'POST':
        host_name = request.form['hostname']
        host_addr = request.form['hostaddr']
        
        if host_addr and host_name:
            try:
                if logic.check_docker_status(docker.APIClient(base_url=host_addr), host_addr):
                    logic.run_insert(ip, port, db, coll, {'host_name': host_name, 'addr': host_addr})
                else:
                    return render_template('add_host.html', error='invalid address')
                       
            except Exception as e:
                    logic.logger(e)
                    return render_template('add_host.html', error='invalid address')
                    
            return render_template('add_host.html')
        else:
            error = 'You must add host address and host name'
            return render_template('add_host.html', error=error)
    
    return render_template('add_host.html')

@app.route('/get_host_list')
def get_host_list():
    return json.dumps(logic.run_threading_host_status(logic.get_hosts_for_sp(ip, port, db, coll)))

@app.route('/')
def dashboard():
    host_addr = request.args.get('host_addr')

    if host_addr:
        return redirect(url_for('index', host_addr=host_addr))  
    
    return render_template('dashboard.html')

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

