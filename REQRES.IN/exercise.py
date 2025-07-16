from locust import HttpUser, task, between
import json
import random
import os
import csv

def load_data_register_from_file(filename):
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