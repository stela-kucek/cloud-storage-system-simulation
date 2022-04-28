# Client-App
This application represents the client for accessing the cloud storage API.
## Setup & run
### Prerequisites
- python3
- pip3
### Run steps
0. (ubuntu only, if venv not installed: `sudo apt install python3-venv`)
1. `python -m venv .env` 
2. on MS Windows: `.env/Scripts/activate`

   on Ubuntu: ` source .env/bin/activate`
3. `pip install -r requirements.txt`
4. `python app.py`
## Input data
The input data used for populating the cloud storage can be found in `movies_metadata.csv`.
## Log report
The `report.txt` file contains logs of a test run with the client app.
