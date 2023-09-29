import base64
import os
import boto3
import logging

logger = logging.getLogger(__name__)

class S3FileManager:
    def __init__(self):
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

        self.session = boto3.Session(
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.s3 = self.session.resource("s3")
        self.bucket = self.s3.Bucket(self.bucket_name)

    def upload_file(self, key, file_content):
        self.bucket.put_object(Key=key, Body=file_content)
        return key

    def delete_file(self, key):
        self.bucket.delete_objects(Delete={"Objects": [{"Key": key}]})
    
    def get_file_content(self,key):
        obj = self.s3.Object(self.bucket_name, key)
        logger.info(f"obj in bucket {obj.__dict__}")
        converted_string = base64.b64encode(obj.get()['Body'].read())
        return converted_string
