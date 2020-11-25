import sys
import os
import pika

rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq',5672))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
result = rabbitMQChannel.queue_declare('', exclusive=True)
queue_name = result.method.queue

rabbitMQChannel.queue_bind(exchange='logs', queue=queue_name, routing_key='log')

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body), file=sys.stderr)

rabbitMQChannel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

rabbitMQChannel.start_consuming()
