from socket import socket, AF_INET, SOCK_STREAM
import json, time

class Client:
    def __init__(self, hid):
        self.hid = hid

    def send_message(self, type, data):
        payload = {
            'type': type,
            'data': data
        }
        self.s.send(json.dumps(payload).encode('utf-8'))

    def connect(self, server='127.0.0.1', port=28591):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.connect((server, port))
        self.send_message('handshake', self.hid)
        time.sleep(10)

    def message_handler(self, message):
        if message['type'] == 'unlock':
            print('Welcome, %s!' % message['data']['user'])
            self.s.send(json.dumps({
                'success': True,
                'message': 'ok'
            }).encode('utf-8'))
        else:
            self.s.send(json.dumps({
                'success': False,
                'message': 'Bad type'
            }).encode('utf-8'))

    def pool(self):
        while True:
            data = json.loads(self.s.recv(8192))
            self.message_handler(data)
