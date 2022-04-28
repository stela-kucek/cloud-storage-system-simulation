# Cloud Storage System Simulation

This project demonstrates the implementation and usage of a distributed storage access structure, namely a hash-based structure (also utilized in, e.g., [Amazon's DynamoDB](https://aws.amazon.com/dynamodb/)) for storing key-value pairs.

The application encompasses the following:
* Permanent storage of key-value pairs
* A dictionary-based data access API
* A client application using the data access API

Want to give this app a run? Skip to the [Installation and Setup](#install) section.

## Application Design
This section describes the overall architecture of the application and the implemented distributed access structure.

### Architecture

This cloud storage system is comprised of two central components:

* Controller
*	Storage server node network

As can be seen in Figure 1, the user accesses the cloud storage using the client application, which in turn communicates with the controller. The controller serves several purposes: 
*	It acts as an intermediary between the client and the storage nodes (i.e., forwards and/or filters user requests)
*	It sets up the network of storage nodes
*	It initializes the system by generating a hash table/index directory and propagating it to all created nodes
*	It collects intermediate results for range queries per node and creates the final result based on the merged values
The storage nodes are Docker containers running within a Docker network, each with its own Docker volume to enable persisting and reusing data. The nodes communicate with each other by forwarding requests to simulate a gossip-like protocol. The index directory is stored on each storage node, which enables quick and cheap access to relevant data. For insert, search, and delete operations, the controller forwards the request to a randomly selected entry point (storage node), and (in the worst case) in the next “hop” the right node is accessed. Furthermore, each storage node uses a JSON file as its bucket (storage file) where the objects are stored as (key, value) pairs.

<p align="center">
  <img src="https://user-images.githubusercontent.com/18488581/165816786-810f3b46-6a60-45f3-a075-be88bd03596d.png"/>
</p>
<p align="center">
  Figure 1 Application architecture overview
</p>

### Distributed access structure

This application implements a hash-based distributed access structure using the following logic. 
The keys in the index are placed on a ring within a certain value range, since it is a ring, the chosen value range is [0-360) – because a circle has 360 degrees. 
As can probably be assumed from this description, the mapping function for positions on the ring looks like this:

<p align="center">
  <img src="https://latex.codecogs.com/svg.image?p(x)=hash(x)&space;%&space;360&space;&space;" title="https://latex.codecogs.com/svg.image?p(x)=hash(x) % 360 " />
</p>

where 
- p(x) represents the position on the ring of key x, 
- hash() is the built-in python hash function, and 
- % is the modulo operator.

The mapping in the application is set up as follows. First, the position of each storage node is calculated and saved. Then, to each key in the directory, the closest storage node in the counterclockwise direction is assigned. A (hopefully) comprehensive illustration of the realization of this access structure is given in Figure 2.

<p align="center">
  <img src="https://user-images.githubusercontent.com/18488581/165819645-f3b94dd2-5c66-45e0-9131-21eb93fce70b.png"/>
</p>

<p align="center">
  Figure 2 Demonstration of hashing mechanism
</p>
  
<section id="install"/>

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

