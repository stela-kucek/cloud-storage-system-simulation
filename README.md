# Cloud Storage System Simulation

This project demonstrates the implementation and usage of a distributed storage access structure, namely a hash-based structure (also utilized in, e.g., [Amazon's DynamoDB](https://aws.amazon.com/dynamodb/)) for storing key-value pairs.

The application encompasses the following:
* Permanent storage of key-value pairs
* A dictionary-based data access API
* A client application using the data access API

## Installation and Setup
This section describes how you can run and test the application locally.

### Prerequisites
* Docker
* Python3
* Pip3

### Download and Run
* Pull or download the 3 folders from this Git repository
  -	Client-App
  -	Controller
  -	Storage-Node
* Make sure Docker is running
* Open a cmd console and pull the image for the storage node by running

  `docker pull a1303858/storage-node`
  
* Navigate to the Controller folder
  - Open cmd and run the following:

    ```sh
    python -m venv .env \
    source .env/bin/activate \
    pip install -r requirements.txt \
    PYTHONHASHSEED=0 python app.py
    ```
* Navigate to the Client-App folder
  - Open cmd and run the following:
    ```sh
    python -m venv .env \
    source .env/bin/activate \
    pip install -r requirements.txt \
    python app.py
    ```
* Within the Client-App folder, the report will be generated as `report.txt` (see an [example report](https://github.com/stela-kucek/cloud-storage-system-simulation/blob/b3cc717ce47e2aa4ff6d815a821cc99f0e332600/Client-App/example-report.txt))

