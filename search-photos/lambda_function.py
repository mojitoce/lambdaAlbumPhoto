import json
import boto3
import requests
from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    bucket_url = 'https://photo-bucket-v4.s3.amazonaws.com/'
    query = event['queryStringParameters']['q'].strip().lower()
   
    # extract es endpoint information
    es_client = boto3.client('es')
    es_endpoint = es_client.describe_elasticsearch_domain(DomainName='photoindexandsearch')['DomainStatus']['Endpoint']
    client = boto3.client('lex-runtime', region_name='us-east-1')
    response = client.post_text(
        botName='search_photos',
        botAlias='prod',
        userId='cesare',
        inputText=query
    )

    # If no slots are filled return an empty array
    if not response.get('slots', False):
        #return empty array of photos
        return {
            'statusCode': 200,
            'body': {}
        }

    slots = response['slots']
    labels = []
    for k, v in slots.items():
        if v:
            labels.append(v)

    # Search labels
    photo_keys = {}
    photo_keys['result'] = []
    urls = set()
    for lab in labels:
        # print(lab)
        get_request_url = 'https://' + es_endpoint + '/photos/_search?q='
        es_response = requests.get(get_request_url+lab, auth=HTTPBasicAuth('coms6998', 'Coms6998!'))
        es_search = json.loads(es_response.content.decode('utf-8'))
        hits = es_search['hits']['hits']
        # print('h', hits)
        if len(hits)==0:
            continue

        for photo in hits:
            if photo['_source']['objectKey'] not in urls:
                photo_keys['result'].append({'url': bucket_url + photo['_source']['objectKey'], "labels":photo['_source']['labels']})
                urls.add(photo['_source']['objectKey'])

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body':  json.dumps(photo_keys)
    }
