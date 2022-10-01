import json
import requests

import requests
from requests.adapters import HTTPAdapter, Retry


class Messenger:
    GRAPH_API_URL = 'https://graph.facebook.com/v15.0/me'

    def __init__(self, access_token):
        self.access_token = access_token

    def send(self, message):
        params = {
            'access_token': self.access_token
        }
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = requests.post(
            f'{self.GRAPH_API_URL}/messages',
            params=params,
            json=message.to_dict()
        )

        if response.status_code != 200:
            print("Error!")
        return response.json()
