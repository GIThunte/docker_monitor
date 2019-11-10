from docker_monitor import app
from datetime import datetime, timedelta
from threading import Thread
from multiprocessing import Queue
from pymongo import MongoClient
from os import environ
import threading
import docker

app_mongo_ip      = environ.get('MONGO_IP', '10.1.0.65')
app_mongo_port    = int(environ.get('MONGO_PORT', '27017'))
app_mongo_db      = environ.get('MONGO_DB', 'host_lists')
app_mongo_coll    = environ.get('MONGO_COLLECTION', 'hosts')

def printLog(func):
    def wrapper(text, *args, **kwargs):
        result = func('{} {}'.format(datetime.now().strftime("%d.%m.%Y - %H:%M:%S"), text), *args, **kwargs)
        return result
    return wrapper

@printLog
def logger(text):
    print(text)

def check_docker_status(connect_obj, host_addr):
    try:
        connect_obj.ping()
        return True
    except Exception as e:
        logger('Could not connect to docker - {}'.format(host_addr))
        return False 

def docker_container_logs(connect_obj, container_id):
    try:
        return connect_obj.logs(container_id)
    except Exception as e:
        logger(e)

def docker_inspect(connect_obj, container_id):
    try:
        return connect_obj.inspect_container(container_id)
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

def get_mongo_connect_obj():
    return {'con_obj': {'app_mongo_ip': app_mongo_ip,
            'app_mongo_port': app_mongo_port,
            'app_mongo_db': app_mongo_db,
            'app_mongo_coll': app_mongo_coll}}

def get_mongo_client(host, port):
    try:
        return MongoClient(host, port)
    except Exception as e:
        logger(e)
    
def get_database(host, port, db_name):
    try:
        return get_mongo_client(host, port)[db_name]
    except Exception as e:
        logger(e)

def get_collection(host, port, db_name, collection_name):
    try:
        return get_database(host, port, db_name)[collection_name]
    except Exception as e:
        logger(e)

def get_hosts_for_sp(host, port, db_name, collection_name):
    json_obj = {}
    collection_obj = get_collection(host, port, db_name, collection_name).find()
    for iter_hosts in collection_obj:
        json_obj[iter_hosts['host_name']] = iter_hosts['addr']
        
    return json_obj

def get_hosts_for_add_hl(host, port, db_name, collection_name):
    return [x for x in get_collection(host, port, db_name, collection_name).find()]

def insert_mongo_data(host, port, db_name, collection_name, insert_data):
    try:
        return get_collection(host, port, db_name, collection_name).insert_one(insert_data).inserted_id
    except Exception as e:
        logger(e)   

def remove_mongo_data(host, port, db_name, collection_name, remove_data):
    try:
        return get_collection(host, port, db_name, collection_name).remove(remove_data)
    except Exception as e:
        logger(e)   

def run_insert(host, port, db_name, collection_name, insert_data):
    if insert_mongo_data(host, port, db_name, collection_name, insert_data):
        return True
    else:
        return False

def check_exits_host(host, port, db_name, collection_name, check_data):
    if get_collection(host, port, db_name, collection_name).find_one(check_data):
        return True
    else:
        return False
