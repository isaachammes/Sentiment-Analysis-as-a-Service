#!/usr/bin/env python3

from flask import Flask, render_template, request, url_for, redirect, jsonify
from hashlib import sha224
import jsonpickle, pickle
import platform
import io, os, sys
import pika
import requests
import json
import pymysql
import time
import redis
import joblib

redisHashToTopic = redis.Redis(host='redis', port=6379, db=1)
redisModel = redis.Redis(host='redis', port=6379, db=2)

lr = joblib.load("lr_sentiment1.joblib")
redisModel.set("model", pickle.dumps(lr))

from model_update import feedback

app = Flask(__name__)

# Rabbitmq and database variables
rhost = 'rabbitmq'
rport = 5672
dhost = 'mysql'
dport = 3306
duser = 'root'
dpass = 'pass'

# Declare echanges for Rabbitmq
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rhost, port=rport))
channel = connection.channel()
channel.exchange_declare(exchange='toWorker', exchange_type='direct')
channel.exchange_declare(exchange='logs', exchange_type='topic')
connection.close()

# Initialize database (id, hash, document, sentiment)
print('Database is being initialized')
db = pymysql.connect(host=dhost, port=dport, user=duser, password=dpass)
cursor = db.cursor()
cursor.execute("DROP DATABASE IF EXISTS db")
cursor.execute("CREATE DATABASE db")
cursor.execute("USE db")
cursor.execute("DROP TABLE IF EXISTS mytable")
cursor.execute("CREATE TABLE mytable(id INT AUTO_INCREMENT PRIMARY KEY, hash VARCHAR(255) NOT NULL UNIQUE, document VARCHAR(1000) NOT NULL, sentiment VARCHAR(20) NOT NULL)")
cursor.execute("SELECT * FROM mytable")
print(cursor.fetchall())
db.commit()
db.close()

# Home route to enter a document to be analyzed
@app.route('/', methods=['GET', 'POST'])
def home():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rhost, port=rport))
    channel = connection.channel()
    channel.basic_publish(exchange='logs', routing_key='log', body="Home endpoint has been accessed")
    if request.method == 'POST':
        channel.basic_publish(exchange='logs', routing_key='log', body="Document has been submitted")
        document = request.form.get('document')
        ha = sha224(document.encode('utf-8')).hexdigest()
        message = {'document': document,'hash': ha}
        message_pickled = jsonpickle.encode(message)
        channel.basic_publish(exchange='toWorker', routing_key='',body=message_pickled)
        channel.basic_publish(exchange='logs', routing_key='log', body="Document is now being analyzed!")

        db = pymysql.connect(host=dhost, port=dport, user=duser, password=dpass, db='db')
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM mytable WHERE hash='{ha}'")
        result = cursor.fetchall()
        db.close()
        # Waiting for database to be updated
        while not result:
            db = pymysql.connect(host=dhost, port=dport, user=duser, password=dpass, db='db')
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM mytable WHERE hash='{ha}'")
            result = cursor.fetchall()
            db.close()
            time.sleep(0.5)
        matching_topics_b = redisHashToTopic.smembers(ha)
        matching_topics = []
        for topic in matching_topics_b:
            matching_topics.append(topic.decode("utf-8"))

        for row in result:
            sentiment = row[3]

        channel.basic_publish(exchange='logs', routing_key='log', body="Sentiment is being returned!")
        connection.close()
        return redirect(url_for('result', document=document, sentiment=sentiment, topic=str(matching_topics)))
    connection.close()
    return render_template('Home.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    document = request.args.get('document', None)
    topic = request.args.get('topic', None)
    sentiment = request.args.get('sentiment', None)
    if request.method == 'POST':
        return redirect(url_for('feedbackroute', document=document, sentiment=sentiment))
    return render_template('result.html', document=document, sentiment=sentiment, topic=topic)

@app.route('/summary', methods=['GET'])
def summary():
    db = pymysql.connect(host=dhost, port=dport, user=duser, password=dpass, db='db')
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM mytable")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM mytable WHERE sentiment='Positive'")
    positive = cursor.fetchone()[0]/total
    cursor.execute("SELECT COUNT(*) FROM mytable WHERE sentiment='Negative'")
    negative = cursor.fetchone()[0]/total
    db.close()
    return render_template('summary.html', total=total, positive=positive, negative=negative)

@app.route('/feedback', methods=['GET', 'POST'])
def feedbackroute():
    document = request.args.get('document', None)
    sentiment = request.args.get('sentiment', None)
    if request.method == 'POST':
        new_sentiment = request.form.get('sentiment').split()
        sent = new_sentiment[0]
        new_doc = " ".join(new_sentiment[1:])
        print(sent, new_doc)
        feedback(str(new_doc), sent)
        return render_template('thankyou.html')
    return render_template('feedback.html', document=document, sentiment=sentiment)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)