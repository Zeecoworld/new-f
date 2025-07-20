import boto3
from django.conf import settings
from botocore.client import Config

def upload_file_to_s3(file, file_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        config=Config(signature_version='s3v4')
    )
    s3_client.upload_fileobj(
        file,
        settings.AWS_STORAGE_BUCKET_NAME,
        file_name,
        ExtraArgs={
            'ContentType': file.content_type,
            'ACL': 'public-read'
        }
    )
    return f"{settings.AWS_S3_ENDPOINT_URL}{settings.AWS_STORAGE_BUCKET_NAME}/{file_name}"
