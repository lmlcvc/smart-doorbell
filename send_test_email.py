#! /usr/bin/python

# Imports
import requests
from mailjet_rest import Client
import os

API_KEY = os.environ['MJ_APIKEY_PUBLIC']
API_SEC = os.environ['MJ_APIKEY_PRIVATE']

mailjet = Client(auth=(API_KEY, API_SEC))

def send_simple_message():
    print("I am sending an email.")
    data = {
        'Messages': [
            {
              "From": {
                "Email": "doorbell@mailjet.com",
                "Name": "Smart Doorbell"
              },
              "To": [
                {
                  "Email": "djelusic@riteh.hr",
                  "Name": "Admin"
                }
              ],
              "Subject": "Mail test subject",
              "TextPart": "Mail test",
              "HTMLPart": "<h3>Mail Test HTML</h3>"
            }
        ]
    }

    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
