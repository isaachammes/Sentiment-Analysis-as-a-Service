#!/usr/bin/env python3

from flask import Flask, request, Response, jsonify
from hashlib import sha224
import jsonpickle, pickle
import platform
import io, os, sys
import pika
import requests
import json
import pymysql

app = Flask(__name__)

rhost = 'rabbitmq'
rport = 5672
dhost = 'mysql'
dport = 3306
duser = 'root'
dpass = 'pass'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rhost, port=rport))
channel = connection.channel()
channel.exchange_declare(exchange='toWorker', exchange_type='direct')
channel.exchange_declare(exchange='logs', exchange_type='topic')
connection.close()

@app.route('/', methods=['GET'])
def hello():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rhost, port=rport))
    channel = connection.channel()
    channel.basic_publish(exchange='logs', routing_key='log', body="The server is running! Use a valid endpoint!")
    connection.close()
    return '<h1> Text Sentiment Analysis Server</h1><p> Use a valid endpoint </p>'

@app.route('/init', methods=['GET'])
def init():
    db = pymysql.connect(host=dhost, port=dport, user=duser, password=dpass)
    cursor = db.cursor()
    cursor.execute("DROP DATABASE IF EXISTS db")
    cursor.execute("CREATE DATABASE db")
    cursor.execute("USE db")
    cursor.execute("DROP TABLE IF EXISTS mytable")
    cursor.execute("CREATE TABLE mytable(hash VARCHAR(255), document VARCHAR(1000), sentiment VARCHAR(20))")
    db.commit()
    db.close()
    response = {"message": "Database successfully initialized!"}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/analyze', methods=['POST'])
def analyze():
    r = request
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rhost, port=rport))
    channel = connection.channel()
    dat = r.data
    doc = json.loads(dat)['document']
    ha = sha224(dat).hexdigest()
    response = {'hash': ha}
    message = {'document': doc,'hash': ha}
    message_pickled = jsonpickle.encode(message)
    channel.basic_publish(exchange='toWorker', routing_key='',body=message_pickled)
    channel.basic_publish(exchange='logs', routing_key='log', body="Document is now being analyzed!")
    
    #    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672))
    #    channel = connection.channel()
    #    channel.basic_publish(exchange='logs', routing_key='log', body="Something went wrong with the server!")
    #    response = {'hash': 'something went wrong'}
    connection.close()
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/get/<string:hahaha>', methods=['GET'])
def haha(hahaha):
    db = pymysql.connect(host=dhost, port=dport, user=duser, password=dpass, db='db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM mytable")
    s = cursor.fetchall()
    print(s)
    response = {"message": s}
    db.close()
    response_json = json.dumps(response)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rhost, port=rport))
    channel = connection.channel()
    channel.basic_publish(exchange='logs', routing_key='log', body="Match is being returned!")
    connection.close()
    return Response(response=response_json, status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)