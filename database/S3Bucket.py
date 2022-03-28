import os
import uuid

import s3_bucket as s3
from s3_bucket import Bucket

from singleton import Singleton


class S3Bucket(metaclass=Singleton):
    def __init__(self):
        aws_access_key = os.getenv("AWS_ACCESS_KEY")
        aws_secret_key = os.getenv("AWS_SECRET_KEY")
        bucket_name = os.getenv("AWS_BUCKET_NAME")

        s3.Bucket.prepare(aws_access_key, aws_secret_key)
        Bucket._get_boto3_resource()
        self._bucket = s3.Bucket(bucket_name)

    def get(self, key: str):
        return self._bucket.get(key)

    def upload(self, data: bytes, content_type: str = str(uuid.uuid4()), key: str = None, folder_prefix: str = ""):
        return self._bucket.put(folder_prefix + key, data, content_type)

    def delete(self, key: str):
        return self._bucket.delete(key)


s3Bucket = S3Bucket()
