from random import randrange
import json
import requests
from flask import Flask, request
import docker
import datetime

docker_client = docker.from_env()
app = Flask(__name__)

directory = {}
server_positions = {}
server_ports = {
    "5001": False,
    "5002": False,
    "5003": False,
    "5004": False,

    "5005": False,
    "5006": False,
    "5007": False,
    "5008": False,
}


###
# ROUTES
###
@app.route('/start')
def start():
    start_storage_nodes(4)
    generate_directory()
    replicate_directory()
    set_successors()
    nodes = list(server_positions.keys())
    storage_files = list(map(get_storage_files, nodes))
    t = get_timestamp()
    return {"timestamp": t, "step": "start", "nodes": nodes, "storage files": storage_files}


@app.route('/insert', methods=['POST'])
def insert():
    data = request.get_json(force=True)
    # select a random server to fw to:
    entry_point = get_random_entry_point()
    return insert_into_storage_node(data, entry_point)


@app.route('/status')
def get_file_status():
    t = get_timestamp()
    status_log = {"timestamp": t, "step": "status after insert", "status log": []}
    for p, taken in server_ports.items():
        if taken:
            res = get_file_status_from_node(p)
            status_log['status log'].append(res.json())
    return status_log


@app.route('/delete', methods=['POST'])
def delete():
    t = get_timestamp()
    log = {"timestamp": t, "step": "delete"}
    data = request.get_json(force=True)
    entry_point = get_random_entry_point()
    res = delete_from_storage_node(data, entry_point)
    log['status'] = json.loads(res.content)
    return log


@app.route('/search')
def search():
    t = get_timestamp()
    data = request.get_json(force=True)
    entry_point = get_random_entry_point()
    result = {"timestamp": t, "step": "search"}
    res = search_in_storage_node(data, entry_point)
    result['result'] = json.loads(res.content)
    return result


@app.route('/range')
def search_range():
    t = get_timestamp()
    data = request.get_json(force=True)
    range_result = {"timestamp": t, "step": "range search", "result": {}}
    intermediate_res = {}
    for p, taken in server_ports.items():
        if taken:
            res = search_range_in_storage_node(data, p)
            intermediate_res.update(json.loads(res.content))
    range_result['result'] = dict(sorted(intermediate_res.items()))
    return range_result
###


###
# ACCESS FUNCTIONS
###
def replicate_directory():
    for p, taken in server_ports.items():
        if taken:
            requests.post('http://localhost:' + str(p) + '/directory', json=json.dumps(directory))


def set_successors():
    for p, taken in server_ports.items():
        if taken:
            res = requests.get('http://localhost:' + str(p) + '/')
            node = res.text
            # node = data['node']
            s = find_successor(node)
            data = {"successor": s}
            res = requests.post('http://localhost:' + str(p) + '/successor', json=data)
            print(res)
            print('successor set for '+node+' and is: '+s)


def insert_into_storage_node(data, node):
    addr = 'http://localhost:' + node + '/insert'
    res = requests.post(addr, json=data)
    return res.json()


def delete_from_storage_node(data, node):
    addr = 'http://localhost:' + node + '/delete'
    return requests.post(addr, json=data)


def search_in_storage_node(data, node):
    addr = 'http://localhost:' + node + '/search'
    return requests.get(addr, json=data)


def search_range_in_storage_node(data, node):
    addr = 'http://localhost:' + node + '/range'
    return requests.get(addr, json=data)


def get_file_status_from_node(node):
    addr = 'http://localhost:' + node + '/status'
    return requests.get(addr)
###


###
# UTIL FUNCTIONS
###
def is_active(port):
    return server_ports[port]


def get_random_entry_point():
    active_nodes = list(filter(is_active, server_ports.keys()))
    idx = randrange(len(active_nodes))
    return active_nodes[idx]


def get_ring_pos(key):
    return hash(key) % 360


def get_storage_files(node: str) -> str:
    return node + '-bucket.json'


def get_timestamp() -> str:
    return '{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now())  # yields format: 2014-Oct-18 21:31:12


def find_successor(node: str) -> str:
    pos = int(server_positions[node])
    i = pos + 1
    count_down = 359
    while count_down >= 0:
        count_down -= 1
        for server, pos in server_positions.items():
            # print('comparing ' + str(pos) + ' and ' + str(i))
            if pos == i:
                return server
        if i == 359:  # we traversed the full ring -> we have to continue from 0
            i = 0
        else:
            i += 1
    return 'error'
###


###
# INITIALIZATION FUNCTIONS
###
def generate_directory():
    print('generating directory...')
    global directory
    p = 0
    while p < 360:
        node = find_closest_node_ccw(p)
        print('setting dir at ' + str(p) + ' to ' + node)
        directory[str(p)] = node
        p += 1
    print('directory generated:')
    print(directory)
    return directory


def find_closest_node_ccw(point: int) -> str:
    i = point
    count_down = 360
    while count_down >= 0:
        count_down -= 1
        for server, pos in server_positions.items():
            # print('comparing ' + str(pos) + ' and ' + str(i))
            if pos == i:
                return server
        if i == 359:  # we traversed the full ring -> we have to continue from 0
            i = 0
        else:
            i += 1
    return 'error'


def get_available_port():
    for p, taken in server_ports.items():
        if not taken:
            return str(p)
    return None


def start_storage_nodes(count=1):
    print('creating network...')
    net = docker_client.networks.create('cloud-storage', driver='bridge')
    print('running containers...')

    for i in range(0, count):
        port = get_available_port()
        if port is not None:
            c_name = 'storage-node-' + str(i)
            pos = get_ring_pos(c_name)
            args = ["node=" + str(i)]
            global server_positions
            server_positions[c_name] = pos
            docker_client.volumes.create(name=c_name, driver='local')  # create volume for persistent storage per node
            global server_ports
            server_ports[port] = True
            docker_client.containers.run('a1303858/storage-node', environment=args, name=c_name, ports={'5000/tcp': port},
                                         volumes={c_name: {'bind': '/usr/src/app', 'mode': 'rw'}},
                                         network=net.name,
                                         detach=True)
        else:
            print('Sorry. No more resources left for storing.')

    print('complete.')
    # reload and print containers
    # net.reload()
    # res = {}
    # i = 0
    # containers = net.containers
    # for c in containers:
    #     res[str(i)] = c.name
    #     print(c.name)
    #     i += 1
    # print(res)
###


if __name__ == '__main__':
    print('running Controller...')
    app.run(host='0.0.0.0')
