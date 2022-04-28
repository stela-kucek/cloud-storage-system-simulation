import json
import sys
import requests
from flask import Flask, request

app = Flask(__name__)

directory = {}
server_id = ''
bucket_id = ''
successor = ''


###
# ROUTES
###
@app.route('/')
def hello_world():
    return server_id


@app.route('/search')
def search():
    data = request.get_json(force=True)
    key = data['key']
    idx = str(get_ring_pos(key))
    if directory[idx] == server_id:
        with open(bucket_id) as bucket:
            store = json.load(bucket)
            if key in store:
                val = store[str(key)]
                msg = "Successfully found value for key '" + str(key) + "'"
                return {"status": "SUCCESS", "message": msg,
                        "node": server_id, "file": bucket_id, "key": key, "value": val}
            else:
                msg = "Could not fetch (k,v) pair. Key '" + str(key) + "' does not exist."
                return {"status": "FAILED", "message": msg, "node": server_id, "file": bucket_id}

    else:
        addr = 'http://' + str(directory[idx]) + ':5000/search'
        print("forwarding to " + addr, flush=True)
        res = forward_to_node(addr, data)
        result_json = json.loads(res.content)
        return result_json


@app.route('/directory', methods=['POST'])
def set_directory():
    data = request.get_json(force=True)
    global directory
    directory = json.loads(data)
    return {"status": "SUCCESS", "message": "Successfully set directory"}


@app.route('/insert', methods=['POST'])
def insert():
    data = request.get_json(force=True)
    key = data['key']
    idx = str(get_ring_pos(key))
    val = data['value']
    if directory[idx] == server_id:
        # TODO: Duplicate the object on the next node
        addr = 'http://' + successor + ':5000/replicate'
        print("replicating to " + addr, flush=True)
        res = forward_to_node(addr, data)
        print(res)
        #
        write_to_bucket(key, val)
        message = "Successfully written (" + str(key) + "," + str(val) + ")"
        return {"status": "SUCCESS", "message": message}
    else:
        addr = 'http://' + str(directory[idx]) + ':5000/insert'
        print("forwarding to " + addr, flush=True)
        res = forward_to_node(addr, data)
        result_json = json.loads(res.content)
        return {"result": result_json}


@app.route('/status')
def status():
    with open(bucket_id) as bucket:
        store = json.load(bucket)
        num_items = len(store.items())
        return {"status": "SUCCESS", "message": "Successfully queried file status.",
                "node": server_id, "file": bucket_id, "number of elements stored": num_items}


@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json(force=True)
    key = data['key']
    idx = str(get_ring_pos(key))
    if directory[idx] == server_id:
        with open(bucket_id) as bucket:
            store = json.load(bucket)
            if key in store:
                val = store.pop(key)
            else:
                msg = "Could not delete (k,v) pair. Key '" + str(key) + "' does not exist."
                return {"status": "FAILED", "message": msg, "node": server_id, "file": bucket_id}
        with open(bucket_id, 'w') as outfile:
            json.dump(store, outfile)
            # also replicate this change to successor:
            addr = 'http://' + successor + ':5000/remove'
            print("also removing from " + addr, flush=True)
            res = forward_to_node(addr, data)
            print(res)
            #
            return {"status": "SUCCESS", "message": "Successfully deleted (k,v) pair.",
                    "node": server_id, "file": bucket_id, "key": key, "value": val}
    else:
        addr = 'http://' + str(directory[idx]) + ':5000/delete'
        print("forwarding to " + addr, flush=True)
        res = forward_to_node(addr, data)
        result_json = json.loads(res.content)
        return {"result": result_json}


@app.route('/range')
def search_range():
    data = request.get_json(force=True)
    key1 = str(data['key1']).lower()
    key2 = str(data['key2']).lower()
    result = {}
    with open(bucket_id) as bucket:
        store = json.load(bucket)
        sorted_data = dict(sorted(store.items()))
        for k, v in sorted_data.items():
            if (min(key1, k.lower()) == key1) and (min(key2, k.lower()) == k.lower()):  # this is an element in range
                result.update({k: sorted_data[k]})
    return result


@app.route('/successor', methods=['POST'])
def set_successor():
    data = request.get_json(force=True)
    global successor
    successor = str(data['successor'])
    return {"status": "SUCCESS"}


@app.route('/replicate', methods=['POST'])
def replicate():
    data = request.get_json(force=True)
    key = data['key']
    val = data['value']
    write_to_bucket(key, val)
    message = "Successfully written (" + str(key) + "," + str(val) + ")"
    return {"status": "SUCCESS", "message": message}


@app.route('/remove', methods=['POST'])
def remove_replica():
    data = request.get_json(force=True)
    key = data['key']
    with open(bucket_id) as bucket:
        store = json.load(bucket)
        if key in store:
            val = store.pop(key)
        else:
            msg = "Could not delete (k,v) pair. Key '" + str(key) + "' does not exist."
            return {"status": "FAILED", "message": msg, "node": server_id, "file": bucket_id}
    with open(bucket_id, 'w') as outfile:
        json.dump(store, outfile)
        return {"status": "SUCCESS", "message": "Successfully deleted replica (k,v) pair.",
                "node": server_id, "file": bucket_id, "key": key, "value": val}

####


def forward_to_node(addr, data):
    try:
        if 'search' in addr:
            return requests.get(addr, json=data)
        else:
            return requests.post(addr, json=data)
    except Exception as e:
        return {"error": {"code": 403, "message": str(e), "status": "DENIED"}}


def write_to_bucket(key, val):
    data = {key: val}
    try:
        with open(bucket_id, 'r') as bucket:
            store = json.load(bucket)
        with open(bucket_id, 'w') as outfile:
            store.update(data)
            json.dump(store, outfile, indent=4)

    except IOError:
        print("File does not exist, creating...")
        with open(bucket_id, 'w') as outfile:
            json.dump(data, outfile, indent=4)


def get_ring_pos(key):
    return hash(key) % 360


if __name__ == '__main__':
    server_id = 'storage-node-' + sys.argv[1]
    print('serverId is: ' + server_id)
    bucket_id = server_id + '-bucket.json'
    print('bucketId is: ' + bucket_id)

    app.run(host='0.0.0.0')
