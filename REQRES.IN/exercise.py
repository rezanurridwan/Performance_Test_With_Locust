from locust import HttpUser, task, between, constant, constant_pacing, events
from locust import LoadTestShape
import json
import random
import os
import csv
from datetime import datetime

def load_data_from_file(filename):
    users = []
    filepath = os.path.join(os.path.dirname(__file__), filename) 
    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                email = row[0].strip()
                password = row[1].strip()
                users.append({'email': email, 'password': password})
    return users

class myStagesShape(LoadTestShape):
    stages = [
        {"duration":5, "users":10, "spawn_rate":10},
        # {"duration":10, "users":15, "spawn_rate":5}
    ]
    def tick(self):
        run_time =self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]
        return None


global_token = {}
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test is starting...")
    global global_token
    
    global_token = {
        "x-api-key": "reqres-free-v1",
    }

class myUser(HttpUser):
    wait_time = between(1,3)
    # wait_time = constant(1)
    # wait_time = constant_pacing(2)
    users = load_data_from_file('data_user.csv')
    user = random.choice(users)
    host = 'https://reqres.in'
    
    def on_start(self):
        self.headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': global_token['x-api-key']
        }
        self.payload = {
        'email': self.user['email'],
        'password': self.user['password']
        }
        response = self.client.post('/api/register', data=json.dumps(self.payload), headers=self.headers)
        if response.status_code == 200:
            id = response.json().get('id')
            token = response.json().get('token')
            print(f"User registered successfully with id': {id}, and token: {token}")
        else:
            print(f"Registration failed with status code: {response.status_code}, response: {response.text}")   

    # @task(2)
    def login(self):
        response = self.client.post('/api/login', data=json.dumps(self.users), headers=self.headers)
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"User logged in successfully with token : {token}")
        else:
            print(f"Login failed with status code: {response.status_code}, response: {response.text}")
    @task(3)
    def list_users(self):
        response = self.client.get('/api/users?page=2', headers=self.headers)
        if response.status_code == 200:
            users = response.json().get('data', [])
            print(f"List of users retrieved successfully: {len(users)} users found.")
        else:
            print(f"Failed to retrieve user list with status code: {response.status_code}, response: {response.text}")
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
   
    def on_stop(self):
        # This method is called when a simulated user stops executing
        print(f"User {self.user['email']} has finished the test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # You can also perform cleanup actions here if needed
