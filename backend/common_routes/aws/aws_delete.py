import boto3
from botocore.exceptions import ClientError
from django.conf import settings

def delete_user_images(id):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )

    try:
        # Get list of all objects in the bucket
        objects_to_delete = []
        paginator = s3.get_paginator('list_objects_v2')
        for result in paginator.paginate(Bucket=settings.AWS_BUCKET):
            if 'Contents' in result:
                objects_to_delete.extend(result['Contents'])

        # Iterate through objects
        for obj in objects_to_delete:
            key = obj['Key']
            # Check if the object's key contains the id
            if id in key:
                # Delete the object
                s3.delete_object(Bucket=settings.AWS_BUCKET, Key=key)

        return True
    except ClientError as e:
        # Handle exceptions
        print("An error occurred:", e)
        return False
