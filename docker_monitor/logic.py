from docker_monitor import app
import docker
from datetime import datetime, timedelta

def printLog(func):
    """
    Add time to text for logging
    """
    def wrapper(text, *args, **kwargs):
        result = func('{} {}'.format(datetime.now().strftime("%d.%m.%Y - %H:%M:%S"), text), *args, **kwargs)
        return result
    return wrapper

@printLog
def logger(text):
    print(text)

def check_docker_status(client_obj):
    try:
        client_obj.ping()
        return True
    except Exception as e:
        logger('Could not connect to docker')
        return False

def docker_container_logs(client_obj, container_id):
    try:
        return client_obj.containers.get(container_id).logs()
    except Exception as e:
        logger(e)

def docker_inspect(client_obj, container_id):
    try:
        return client_obj.inspect_container(container_id)
    except Exception as e:
        logger(e)
   
def get_containers(connect_obj):
    try:
        return connect_obj.containers.list(all=True)
    except Exception as e:
        logger(e)

def container_list(connect_obj):
    try:
        return [{'name': x.name, 'id': x.short_id, 'status': x.status } for x in get_containers(connect_obj)]
    except Exception as e:
        logger(e)
    