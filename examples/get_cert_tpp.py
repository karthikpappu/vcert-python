#!/usr/bin/env python3
from vcert import TPPConnection
from vcert.common import build_request
from pprint import pprint
from os import environ
import logging
import random, string

logging.basicConfig(level=logging.DEBUG)

USER = (environ['TPPUSER'])
PASSWORD = (environ['TPPPASSWORD'])
URL = (environ['TPPURL'])
ZONE = (environ['TPPZONE'])


def main():
    print("Tring to ping url",URL)
    conn = TPPConnection(USER,PASSWORD,URL)
    status = conn.ping()
    print("Server online:", status)
    if not status:
        print('Server offline')
        exit(1)

    req = {

    }
    request = build_request("US", "Moscow", "Moscow", "Venafi", "", randomword(10)+".venafi.example.com")
    request_id = conn.request_cert(request)
    cert = conn.retrieve_cert(cert)
    pprint(conn.make_request_and_wait_certificate(request, ZONE))

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

if __name__ == '__main__':
    main()