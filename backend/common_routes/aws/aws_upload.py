import os
import boto3
import tempfile
from botocore.exceptions import ClientError
from django.conf import settings
from django.http import JsonResponse

def upload_to_aws(file_object, bucket_name, file_name, folder_name):
    main_project_bucket_folder_name = "etoolsbuddy"
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )

    try:
        # Check if the folder "images" exists in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{main_project_bucket_folder_name}/")
        if 'Contents' not in response:
            # Folder doesn't exist, create it
            s3.put_object(Bucket=bucket_name, Key=f"{main_project_bucket_folder_name}/")

        # Check if the folder with provided folder_name exists inside "etools"
        folder_key = f"{main_project_bucket_folder_name}/{folder_name}/"
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)
        if 'Contents' not in response:
            # Folder doesn't exist, create it
            s3.put_object(Bucket=bucket_name, Key=folder_key)

        # Upload the file to AWS S3 within the "images" folder
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write the contents of the file object to the temporary file
            temp_file.write(file_object.read())
            temp_file.seek(0)  # Reset file pointer position to the beginning
        
        # Upload the temporary file to AWS S3
        with open(temp_file.name, 'rb') as data:
            s3.upload_fileobj(data, bucket_name, f'{main_project_bucket_folder_name}/{folder_name}/{file_name}')
        
        # Delete the temporary file
        os.unlink(temp_file.name)
        
        object_url = f"{settings.AWS_URL}{main_project_bucket_folder_name}/{folder_name}/{file_name}"
        return object_url
    except ClientError as e:
        return JsonResponse({"error": "An error occurred during image uploading. Please try again"}, status=500)





