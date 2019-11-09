"""
Routes and views for the flask application.
"""
from datetime import datetime
from flask import render_template, request, json, redirect, url_for
from docker_monitor import app
from docker_monitor import logic
from jinja2 import Template
import docker
import json

mongo_con_obj = logic.get_mongo_connect_obj()['con_obj']

ip    = mongo_con_obj['app_mongo_ip']
port  = mongo_con_obj['app_mongo_port']
db    = mongo_con_obj['app_mongo_db']
coll  = mongo_con_obj['app_mongo_coll']

@app.route('/add_new_host', methods=['GET', 'POST'])
def add_new_host():
    if request.method == 'POST':
        host_name = request.form['hostname']
        host_addr = request.form['hostaddr']
        
        if host_addr and host_name:
            try:
                if logic.check_docker_status(docker.APIClient(base_url=host_addr), host_addr):
                    if not logic.check_exits_host(ip, port, db, coll, {'host_name': host_name, 'addr': host_addr}):
                        logic.run_insert(ip, port, db, coll, {'host_name': host_name, 'addr': host_addr})
                    else:
                        return render_template('add_host.html', error='Host is exists')
                else:
                    return render_template('add_host.html', error='Invalid host address')
                       
            except Exception as e:
                    logic.logger(e)
                    return render_template('add_host.html', error='Invalid address or host not accessible')
                    
            return render_template('add_host.html')
        else:
            error = 'You must add host address and host name'
            return render_template('add_host.html', error=error)
    
    return render_template('add_host.html')

@app.route('/get_host_list')
def get_host_list():
    return json.dumps(logic.run_threading_host_status(logic.get_hosts_for_sp(ip, port, db, coll)))

@app.route('/get_all_list')
def get_all_list():
    all_hosts = logic.get_hosts_for_sp(ip, port, db, coll)
    return json.dumps([{'host_name': x, 'addr': all_hosts[x]} for x in all_hosts])

@app.route('/delete_host')
def delete_host():
    host_name = request.args.get('host_name')

    if host_name:
        logic.remove_mongo_data(ip, port, db, coll, {'host_name': host_name})

    return redirect(url_for('add_new_host'))

@app.route('/ping')
def ping():
    host_addr = request.args.get('host_addr')
    try:
        if host_addr and logic.check_docker_status(docker.APIClient(base_url=host_addr), host_addr):
            return {'ping_status': True}
        else:
            return {'ping_status': False}    
    except Exception as e:
        return {'ping_status': False} 
        logic.logger(e)

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

