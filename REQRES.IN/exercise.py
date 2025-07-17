from locust import HttpUser, task, between
import json
import random
import os
import csv

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

class myUser(HttpUser):
    wait_time = between(1,3)
    users = load_data_from_file('data_user.csv')
    user = random.choice(users)
    host = 'https://reqres.in'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': 'reqres-free-v1'
    }
    payload = {
        'email': user['email'],
        'password': user['password']
    }

    @task(1)
    def register(self):
        response = self.client.post('/api/register', data=json.dumps(self.payload), headers=self.headers)
        if response.status_code == 200:
            id = response.json().get('id')
            token = response.json().get('token')
            print(f"User registered successfully with id': {id}, and token: {token}")
        else:
            print(f"Registration failed with status code: {response.status_code}, response: {response.text}")   

    @task(2)
    def login(self):
        response = self.client.post('/api/login', data=json.dumps(self.payload), headers=self.headers)
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
   
