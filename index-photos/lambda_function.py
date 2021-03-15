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

    # print(HTTPBasicAuth('c', 'd'))
    # When I have more infor implement x-amz-meta-customLabels
    metadata_resp = s3_client.head_object(Bucket = bucket, Key = name)
    print(metadata_resp)
    print(metadata_resp.keys())
    
    custom_label = metadata_resp['Metadata']['customlabels']
    custom_label = [x.strip().lower() for x in custom_label.split(',')]
    print(custom_label)

    #{'Labels': [{'Name': 'Hound', 'Confidence': 95.22135162353516, 'Instances': [], 'Parents': [{'Name': 'Dog'}, {'Name': 'Pet'}, {'Name': 'Canine'}]}, {'Name': 'Dog', 'Confidence': 95.22135162353516, 'Instances': [{'BoundingBox': {'Width': 0.692852795124054, 'Height': 0.6309356689453125, 'Left': 0.07569825649261475, 'Top': 0.0567517913877964}, 'Confidence': 94.92607879638672}], 'Parents': [{'Name': 'Pet'}, {'Name': 'Canine'}]}, {'Name': 'Canine', 'Confidence': 95.22135162353516, 'Instances': [], 'Parents': []}, {'Name': 'Pet', 'Confidence': 95.22135162353516, 'Instances': [], 'Parents': []}, {'Name': 'Strap', 'Confidence': 87.1478042602539, 'Instances': [], 'Parents': []}], 'LabelModelVersion': '2.0', 'ResponseMetadata': {'RequestId': 'bf8b1644-cbe7-4cc2-9533-e189859d0e24', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'application/x-amz-json-1.1', 'date': 'Mon, 22 Feb 2021 20:45:21 GMT', 'x-amzn-requestid': 'bf8b1644-cbe7-4cc2-9533-e189859d0e24', 'content-length': '647', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}
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

    url = 'https://search-photo-v2-eho6yb26z6kbhyeouo3s32dexm.us-east-1.es.amazonaws.com/'
    
    post_request_url = url + 'photos/photo'
    r = requests.post(post_request_url, auth=HTTPBasicAuth('coms6998', 'Coms6998!'), json=es_dict)

    print(r)
    
    return {
        'statusCode': 200,
        'body': 'Photo has been added to the index'
    }
