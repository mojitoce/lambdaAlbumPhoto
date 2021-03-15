import boto3

def get_rekog_labels(bucket, name):
    rekog_client = boto3.client('rekognition', region_name='us-east-1')
    rekog_resp = rekog_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': name
                }
            },
            MaxLabels=5,
            )

    labels = []
    for label in rekog_resp['Labels']:
        labels.append(label['Name'])

    return labels
