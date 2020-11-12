from base64 import b64encode, decode
from datetime import datetime
from uuid import uuid4

import websocket
import threading

import json

from ..config import config

# Code adapted from https://aws.amazon.com/blogs/mobile/appsync-websockets-python/


class WebSocket(object):
    def __init__(self, auth=None):

        # Subscription ID (client generated)
        self.sub_id = None

        self.auth = None
        self.access_token = None
        self.api_header = None
        self.gql_subscription = None
        self.api_url = config['aws_appsync_graphqlEndpoint']

        # Discovered values from the AppSync endpoint (API_URL)
        self.wss_url = self.api_url.replace('https', 'wss').replace(
            'appsync-api', 'appsync-realtime-api')
        self.host = self.api_url.replace(
            'https://', '').replace('/graphql', '')

        # Set up Timeout Globals
        # Might delete, depends how i'm feeling
        self.timeout_timer = None
        self.timeout_interval = 10

        if self.auth:
            self.attach_auth(auth)

    def attach_auth(self, auth):
        self.auth = auth
        self.access_token = str(self.auth.access_token)
        self.sub_id = str(self.auth.username)

        self.api_header = {
            'host': self.host,
            'Authorization': self.access_token
        }

    def header_time(self):
        '''Calculate UTC time in ISO format (AWS Friendly): YYYY-MM-DDTHH:mm:ssZ'''
        return datetime.utcnow().isoformat(sep='T', timespec='seconds') + 'Z'

    def header_encode(self, header_obj):
        '''Encode Using Base 64'''
        return b64encode(json.dumps(header_obj).encode('utf-8')).decode('utf-8')

    def reset_timer(self,  ws):
        '''reset the keep alive timeout daemon thread'''

        if self.timeout_timer:
            self.timeout_timer.cancel()
        timeout_timer = threading.Timer(timeout_interval, lambda: ws.close())
        timeout_timer.daemon = True
        timeout_timer.start()

    def on_message(self, ws, message):
        '''Socket Event Callbacks, used in WebSocketApp Constructor'''

        print('### message ###')
        print('<< ' + message)

        message_object = json.loads(message)
        message_type = message_object['type']

        if(message_type == 'ka'):
            reset_timer(ws)

        elif(message_type == 'connection_ack'):
            timeout_interval = int(json.dumps(
                message_object['payload']['connectionTimeoutMs']))

            register = {
                'id': self.sub_id,
                'payload': {
                    'data': self.gql_subscription,
                    'extensions': {
                        'authorization': {
                            'host': self.host,
                            'Authorization': self.access_token
                        }
                    }
                },
                'type': 'start'
            }
            start_sub = json.dumps(register)
            print('>> ' + start_sub)
            ws.send(start_sub)

        elif(message_type == 'data'):
            deregister = {
                'type': 'stop',
                'id': self.sub_id
            }

        elif(message_object['type'] == 'error'):
            print('Error from AppSync: ' + message_object['payload'])

    def on_error(self, ws, error):
        print('### error ###')
        print(error)

    def on_close(self, ws):
        print('### closed ###')

    def on_open(self, ws):
        print('### opened ###')
        init = {
            'type': 'connection_init'
        }
        init_conn = json.dumps(init)
        print('>> ' + init_conn)
        ws.send(init_conn)

    def connect(self, query, variables):

        if not self.auth:
            raise UserWarning(
                "No auth object attached.")

        if self.auth.check_token():
            self.attach_auth(self.auth)

        self.gql_subscription = json.dumps({
            'query': query,
            'variables': variables
        })

        connection_url = self.wss_url + '?header=' + \
            self.header_encode(self.api_header) + '&payload=e30='

        print('Connecting...')

        ws = websocket.WebSocketApp(connection_url,
                                    subprotocols=['graphql-ws'],
                                    on_message=lambda ws, msg: self.on_message(
                                        ws, msg),
                                    on_error=lambda ws, msg: self.on_error(
                                        ws, msg),
                                    on_close=lambda ws:     self.on_close(ws),
                                    on_open=lambda ws:     self.on_open(ws))

        ws.run_forever()
