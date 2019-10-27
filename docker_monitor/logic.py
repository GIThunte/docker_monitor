from docker_monitor import app
import docker

def docker_container_logs(client_obj, container_id):
    return(client_obj.containers.get(container_id).logs())

def docker_inspect(client_obj, container_id):
    return(client_obj.inspect_container(container_id))

def get_containers(connect_obj):
    return(connect_obj.containers.list(all=True))

def container_list(connect_obj):
    return([{'name': x.name, 'id': x.short_id, 'status': x.status } for x in get_containers(connect_obj)])
