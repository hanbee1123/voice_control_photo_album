import json
import boto3
from botocore.vendored import requests
import time
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    
    # # Use rekognition to detect labels
    print("CODE TESTER")
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    key_name = s3_info['object']['key']
    client = boto3.client('rekognition')
    pass_object = {'S3Object':{'Bucket':bucket_name,'Name':key_name}}
    resp = client.detect_labels(Image=pass_object)

    timestamp =time.time()
    labels = []
    #temp = resp['Labels'][0]['Name']
    for i in range(len(resp['Labels'])):
        labels.append(resp['Labels'][i]['Name'])
    
    
    print("DEBUG: LABELS:", labels)
    # Upload data to Elastic Search 
    document = {
        'ObjectKey':key_name,
        'Bucket':bucket_name,
        'timestamp':timestamp,
        'labels':labels
    }
    
    print("DEBUG:", format)
    host = 'URL' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-east-1' # e.g. us-west-1
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    
    es.index(index="images", doc_type="_doc", id=key_name, body=document)
    
    print(es.get(index="images", doc_type="_doc", id=key_name))
