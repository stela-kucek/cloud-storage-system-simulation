import csv
import json
import requests


def start_system():
    addr = 'http://localhost:5000/start'
    res = requests.get(addr)
    report(res.json())


def read_from_csv_and_insert_json(csv_file):
    with open(csv_file, encoding="utf8") as csv_f:
        csv_reader = csv.DictReader(csv_f)
        count = 25
        for rows in csv_reader:
            if count == 0:
                break
            count -= 1
            r_id = rows['title']
            obj_to_store = {
                "key": r_id,
                "value": rows
            }
            addr = 'http://localhost:5000/insert'
            requests.post(addr, json=obj_to_store)


def status():
    addr = 'http://localhost:5000/status'
    res = requests.get(addr)
    report(res.json())


def search(keys: []):
    addr = 'http://localhost:5000/search'
    for k in keys:
        req = {"key": k}
        res = requests.get(addr, json=req)
        report(res.json())


def range_search(key1, key2):
    addr = 'http://localhost:5000/range'
    req = {
        "key1": key1,
        "key2": key2
    }
    res = requests.get(addr, json=req)
    report(res.json())


def delete(keys: []):
    addr = 'http://localhost:5000/delete'
    for k in keys:
        req = {"key": k}
        res = requests.post(addr, json=req)
        report(res.json())


def report(data):
    with open('report.txt', 'a') as json_f:
        json_f.write(json.dumps(data, indent=4) + '\n')


if __name__ == '__main__':
    print("running client app...")
    start_system()
    read_from_csv_and_insert_json('movies_metadata.csv')
    status()
    search(['Toy Story', 'Salt', 'Deadpool'])
    delete(['Toy Story', 'Heat', 'Jumanji'])
    range_search('Anna', 'Division')
    # search(['Assassins', 'Balto', 'Casino', 'Copycat', 'Cutthroat Island'])