#
# Worker server
#
import pickle
import platform
import os
import sys
import pika
import hashlib
import json
import pymysql

hostname = platform.node()

rhost = 'rabbitmq'
rport = 5672
dhost = 'mysql'
dport = 3306
duser = 'root'
dpass = 'pass'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rhost, port=rport))
channel = connection.channel()
channel.exchange_declare(exchange='toWorker', exchange_type='direct')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='toWorker', queue=queue_name, routing_key='')

def callback(ch, method, properties, body):
    message = json.loads(body)
    ha = message['hash']
    doc = message['document']
    db = pymysql.connect(host=dhost, port=dport, user=duser, password=dpass, db='db')
    cursor = db.cursor()
    cursor.execute(f"INSERT IGNORE INTO mytable(hash, document, sentiment) VALUES('{ha}', '{doc}', 'positive')")
    db.commit()
    db.close()
    print("message has been received!", ha, doc)
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)
channel.start_consuming()
