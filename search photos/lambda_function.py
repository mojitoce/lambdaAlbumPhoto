import json
import boto3
import requests
from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    
    bucket_url = 'https://photos-bucketb2.s3.amazonaws.com/'
    # print(event)
    query = event['params']['querystring']['q'].strip().lower()
    
    client = boto3.client('lex-runtime', region_name='us-east-1')
    response = client.post_text(
        botName='search_photos',
        botAlias='prod',
        userId='cesare',
        # sessionAttributes={
        #     'string': 'string'
        # },
        # requestAttributes={
        #     'string': 'string'
        # },
        inputText=query
    )
    
    # print(responsea)
    if not response.get('slots', False):
        #return empty array of photos
        return {
            'statusCode': 200,
            'boday': {}
        }
        
        
    
    slots = response['slots']

    # Eventually download nltk and lemmatize
    # Has to deal with None
    labels = []
    for k, v in slots.items():
        if v:
            labels.append(v)
    
    photo_keys = {}
    photo_keys['result'] = []
    for lab in labels:
        # print(lab)
        get_request_url = 'https://search-photo-v2-eho6yb26z6kbhyeouo3s32dexm.us-east-1.es.amazonaws.com/photos/_search?q='
        es_response = requests.get(get_request_url+lab, auth=HTTPBasicAuth('coms6998', 'Coms6998!'))
        es_search = json.loads(es_response.content.decode('utf-8'))
        # print(es_search)
        hits = es_search['hits']['hits']
        # print('h', hits)
        if len(hits)==0:
            continue
        
        for photo in hits:
            print(photo)
            photo_keys['result'].append({'url': bucket_url + photo['_source']['objectKey'], "labels":[lab]})
        
    # print(photo_keys)


    #  Notice that you need to return the URL, so please append the s3 bucket URL as prefix, e.g.
    # 'https://<bucket_name>.s3.amazonaws.com/' + objectkey


    return {
        'statusCode': 200,
        'body':  json.dumps(photo_keys) 
    }
