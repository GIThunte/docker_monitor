from docker_monitor import app
from datetime import datetime, timedelta
from threading import Thread
from multiprocessing import Queue
import threading
import docker

def printLog(func):
    def wrapper(text, *args, **kwargs):
        result = func('{} {}'.format(datetime.now().strftime("%d.%m.%Y - %H:%M:%S"), text), *args, **kwargs)
        return result
    return wrapper

@printLog
def logger(text):
    print(text)

def check_docker_status(client_obj, host_addr):
    try:
        client_obj.ping()
        return True
    except Exception as e:
        logger('Could not connect to docker - {}'.format(host_addr))
        return False 

def docker_container_logs(client_obj, container_id):
    try:
        return client_obj.logs(container_id)
    except Exception as e:
        logger(e)

def docker_inspect(client_obj, container_id):
    try:
        return client_obj.inspect_container(container_id)
    except Exception as e:
        logger(e)

def get_containers(connect_obj):
    try:
        return connect_obj.containers(all=True)
    except Exception as e:
        logger(e)

def get_image_history(connect_obj, image_name):
    try:
        return [x['CreatedBy'] for x in connect_obj.history(image_name)]
    except Exception as e:
        logger(e)

def container_list(connect_obj):
    try:
        return [{'image':    x['Image'],
                 'name':     x['Names'],
                 'short_id': x['Id'][:12],
                 'status':   x['Status'],
                 'id':       x['Id']}
                 for x in get_containers(connect_obj)]

    except Exception as e:
        logger(e)
    
def get_status_hosts(name_host, address_host, return_out):
    return_out.put({'host_name': name_host,
            'addr': address_host,
            'status': check_docker_status(docker.APIClient(base_url=address_host), host_addr=address_host)})

def run_threading_host_status(host_lists):

    threads     = []
    out_status  = []
    get_threads = Queue()

    for host in host_lists:
        threadObj = Thread(target=get_status_hosts,
                    args=(host, host_lists[host], get_threads),
                    name=host)

        threads.append(threadObj)
        threadObj.start()
    
    for threadObj in threads:
        threadObj.join()
        out_status.append(get_threads.get())

    return out_status
