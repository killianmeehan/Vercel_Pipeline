import urllib3
import requests
import json
import os
from google.oauth2 import service_account
from apiclient import discovery
from http.server import BaseHTTPRequestHandler


API_KEY = os.environ.get('STOCK_API_KEY')


def get_data_lambda():
    http = urllib3.PoolManager()
    url = f"https://cloud.iexapis.com/stable/stock/aapl/previous?token={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()  # raises exception when not a 2xx response
    if response.status_code != 204:
        return response.json()


get_data_lambda()


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1dCcOezsTW8oWa1nIz8QMz2S5gNz0_Op1N_fGue7brlE'
SAMPLE_RANGE = 'A1:AA1000'


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        s = self.path
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        values = get_data_lambda()
        service_account_credentials = {
            "type": os.environ.get("TYPE"),
            "project_id": os.environ.get("PROJECT_ID"),
            "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
            "private_key": os.environ.get("PRIVATE_KEY"),
            "client_email": os.environ.get("CLIENT_EMAIL"),
            "client_id": os.environ.get("CLIENT_ID"),
            "auth_uri": os.environ.get("AUTH_URI"),
            "token_uri": os.environ.get("TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER"),
            "client_x509_cert_url": os.environ.get("CLIENT_URL")
        }
        credentials = service_account.Credentials.from_service_account_info(
            service_account_credentials, scopes=SCOPES)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        values_list = list(values.values())
        final_list = []
        final_list.append(values_list["date"], values_list["close"])
        dict_me = dict(values=final_list)
        service.spreadsheets().values().append(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            valueInputOption='RAW',
            range=SAMPLE_RANGE,
            body=dict_me).execute()

        print('Sheet successfully Updated')
        return
