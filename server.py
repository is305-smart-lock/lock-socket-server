from socketserver import BaseRequestHandler, ThreadingTCPServer
import multiprocessing
import json
import os
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Lock
import threading
from queue import Queue
import pika

load_dotenv(find_dotenv())

DB_CONNECT_STRING = 'mysql+pymysql://%s:%s@%s/%s' % (os.environ.get('MYSQL_USER'),
                                                     os.environ.get('MYSQL_PASSWORD'),
                                                     os.environ.get('MYSQL_SERVER'),
                                                     os.environ.get('MYSQL_DATABASE'))

engine = create_engine(DB_CONNECT_STRING)
DB_Session = sessionmaker(bind=engine)
session = DB_Session()


lock_device_list = []

def construct_message(type, data):
    return json.dumps({
        'type': type,
        'data': data
    }).encode('utf-8')

def mq_message_handler(message):
    if message['type'] == 'list_online_locks':
        return lock_device_list
    else:
        return 'bad type'

def php_communication_thread():
    credentials = pika.PlainCredentials(os.environ.get('RABBITMQ_USER'), os.environ.get('RABBITMQ_PASSWORD'))

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.environ.get('RABBITMQ_SERVER'), credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='locker', exclusive=False)

    def on_request(ch, method, props, body):
        response = mq_message_handler(json.loads(body))
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id= \
                                                             props.correlation_id),
                         body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='locker', on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()


class LockHandler(BaseRequestHandler):
    hid = ''
    def start_mq_listener(self):
        # Start Mq listener
        credentials = pika.PlainCredentials(os.environ.get('RABBITMQ_USER'), os.environ.get('RABBITMQ_PASSWORD'))

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.environ.get('RABBITMQ_SERVER'), credentials=credentials))
        channel = connection.channel()

        channel.queue_declare(queue='locker.%s' % self.hid, exclusive=False)
        channel.confirm_delivery()

        def on_request(ch, method, props, body):
            type = json.loads(body)['type']

            if type == 'unlock':
                self.request.send(json.dumps({
                    'type': 'unlock',
                    'data': {
                        'user': json.loads(body)['data']['user']
                    }
                }).encode('utf-8'))

                ret = json.loads(self.request.recv(8192))
                response = {'success': ret['success'], 'message': 'ok'}
            else:
                response = {'success': False, 'message': 'Bad type'}


            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id= \
                                                                 props.correlation_id),
                             body=json.dumps(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='locker.%s' % self.hid, on_message_callback=on_request)
        channel.start_consuming()


    def handshake(self):
        handshake = self.request.recv(8192)
        if not handshake:
            self.request.close()
            return

        handshake = json.loads(handshake)
        if not session.query(Lock).filter(Lock.hid == handshake['data']).count():
            print('Bad hid: ', self.client_address)
            self.request.close()
            return

        print('handshake success.')

        self.hid = handshake['data']
        # self.request.send(construct_message('handshake', 'ok'))
        if not handshake['data'] in lock_device_list: lock_device_list.append(handshake['data'])
        self.start_mq_listener()

    def handle(self):
        print('Lock handshake: ', self.client_address)
        self.handshake()

    def finish(self):
        print('Lock offline: ', self.client_address)
        if self.hid in lock_device_list: lock_device_list.remove(self.hid)


if __name__ == '__main__':
    t = threading.Thread(target=php_communication_thread)
    t.start()

    serv = ThreadingTCPServer(('', 28591), LockHandler)
    serv.serve_forever()