# Controller
This is an application managing the cloud storage instances and serving the client.
## Setup & run
### Prerequisites
- docker
- python3
- pip3
### Run steps
0. (ubuntu only, if venv not installed: `sudo apt install python3-venv`)
1. `docker pull a1303858/storage-node`
2. `python -m venv .env` 
3. on MS Windows: `.env/Scripts/activate`

   on Ubuntu: ` source .env/bin/activate`
4. `pip install -r requirements.txt`
5. `PYTHONHASHSEED=0 python app.py`
