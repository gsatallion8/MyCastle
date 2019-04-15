from __future__ import print_function

import boto3
import time
import json
import urllib

region = 'us-east-1'

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
# rekognition = boto3.client('rekognition', region)
sns = boto3.client('sns')

threshold = 82

def compare_faces(bucket, key, bucket_target, key_target, threshold=80, region="eu-east-1"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.compare_faces(
	    SourceImage={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		TargetImage={
			"S3Object": {
				"Bucket": bucket_target,
				"Name": key_target,
			}
		},
	    SimilarityThreshold=threshold,
	)
	return response['SourceImageFace'], response['FaceMatches']

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    
    # source_bucket = 'citadel19'
    # key = 'whitewalker.jpg'
    
    s3_path = 'result.txt'
    
    target_list = []
    my_bucket = s3.Bucket(source_bucket)

    for object in my_bucket.objects.all():
        if('family_member' in object.key):
            target_list.append(object.key)
    
    # print(target_list)
    
    for target in target_list:
        
        source_face, matches = compare_faces(source_bucket, key, source_bucket, target, threshold, region)
        
        if(len(matches) == 0):
            continue
        else:
            similarity_score = matches[0]['Similarity']
            result = 'yes'
            name = target.split('_')[2].split('.')[0]
            
            encoded_string = result + '\n' + name
            encoded_string = encoded_string.encode('utf-8')
            
            s3.Bucket(source_bucket).put_object(Key=s3_path, Body=encoded_string)
            
            break
    
    if(len(matches) == 0):
        result = 'no'
        
        encoded_string = result
        encoded_string = encoded_string.encode('utf-8')
        
        s3.Bucket(source_bucket).put_object(Key=s3_path, Body=encoded_string)
        
        url = s3_client.generate_presigned_url('get_object',Params = {'Bucket': source_bucket, 'Key': key})
        
        print(url)
        
        response = sns.publish(TopicArn='arn:aws:sns:us-east-1:892754807653:Intruder-Alarm',Message='Hey! There\'s a white walker at the wall. Here\'s an image of it:' + url)
        # response = sns.publish(PhoneNumber='+41788846303',Message='Hey! There\'s an intruder at your house. Here\'s a link to an image of him: https://s3.us-east-2.amazonaws.com/' + source_bucket + '/' + key )
        # Print out the response
        print(response)
    
    return "Hello from lambda using python"