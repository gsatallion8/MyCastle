from __future__ import print_function

import boto3

import json
import requests

s3 = boto3.client('s3')


def lambda_handler(event, context):
    
    print('Initialized')

    #host = "http://192.168.0.100/api"

    #req = requests.post(host, json = {"devicetype":"my_hue_app#iphone peter"})
    #print(req.status_code)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    response = s3.get_object(Bucket=bucket, Key=key)
    var = response['Body'].read().decode('utf-8')
    host = 'http://192.168.0.100/api/iYVeQ84haW1WRFhxRYUjszNnfl8iLO8eLtLFAv41/lights/2/state'
    if(var[0:2] == 'no'):
        req = requests.request(method = 'PUT', url=host, json = {"xy":[0.6484272236872118, 0.330856101472778], "bri":254})
        print(req.status_code)
    elif('yes' in var):
        req = requests.request(method = 'PUT',url=host, json =  {"xy":[0.330856101472778, 0.6484272236872118], "bri":254})
        print(req.status_code)

    return 'Hello World!'