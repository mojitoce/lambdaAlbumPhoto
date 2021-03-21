import json
import boto3
import botocore
from datetime import datetime
from get_rekog_labels import get_rekog_labels
import requests
from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    s3_client = boto3.client('s3', region_name='us-east-1')

    s3_info = event['Records'][0]['s3']
    bucket = s3_info['bucket']['name']
    name = s3_info['object']['key']

    # extract es endpoint information
    es_client = boto3.client('es', region_name='us-east-1')
    es_endpoint = es_client.describe_elasticsearch_domain(DomainName='photoindexandsearch')['DomainStatus']['Endpoint']

    # Extract custom labels
    metadata_resp = s3_client.head_object(Bucket = bucket, Key = name)
    custom_label = metadata_resp['Metadata']['customlabels']
    custom_label = [x.strip().lower() for x in custom_label.split(',')]


    # Extract rekog labels
    labels = get_rekog_labels(bucket, name)
    labels.extend(custom_label)
    labels = list(set(labels))
    print(labels)

    time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4])

    es_dict = {
        "objectKey": name,
        "bucket": bucket,
        "createdTimestamp": time,
        "labels": labels
    }


    post_request_url = 'https://' + es_endpoint + '/photos/photo'
    r = requests.post(post_request_url, auth=HTTPBasicAuth('coms6998', 'Coms6998!'), json=es_dict)

    print(r)

    return {
        'statusCode': 200,
        'body': 'Photo has been added to the index'
    }
