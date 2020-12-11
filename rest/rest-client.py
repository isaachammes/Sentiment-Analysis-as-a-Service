#!/usr/bin/env python3
# 
#
# A sample REST client for the face match application
#
import requests
import json
import time
import sys, os
import jsonpickle

def analyze(addr, doc, debug=False):
    # prepare headers for http request
    headers = {'content-type': 'application/json'}
    # send http request with image and receive response
    url = addr + '/analyze'
    data = jsonpickle.encode({ "document" : doc})
    response = requests.post(url, data=data, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def init(addr, debug=False):
    url = addr + "/init"
    response = requests.get(url)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def get(addr, ha, debug=False):
    url = addr + "/get/" + ha
    response = requests.get(url)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

host = sys.argv[1]
cmd = sys.argv[2]

addr = 'http://{}'.format(host)

if cmd == 'analyze':
    doc = sys.argv[3]
    reps = int(sys.argv[4])
    start = time.perf_counter()
    for x in range(reps):
        analyze(addr, doc, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'get':
    ha = sys.argv[3]
    get(addr, ha, True)
elif cmd == 'init':
    analyze(addr, True)
else:
    print("Unknown option", cmd)