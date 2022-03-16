import os
import uuid

import s3_bucket as s3

from singleton import Singleton


class S3Bucket(metaclass=Singleton):
    def __init__(self):
        aws_access_key = os.getenv("AWS_ACCESS_KEY")
        aws_secret_key = os.getenv("AWS_SECRET_KEY")
        bucket_name = os.getenv("AWS_BUCKET_NAME")

        s3.Bucket.prepare(aws_access_key, aws_secret_key)
        self._bucket = s3.Bucket(bucket_name)

    def get(self, key: str):
        return self._bucket.get(key)

    def upload(self, data: bytes, content_type: str = None, key: str = None):
        if key is None:
            key = str(uuid.uuid4())

        return self._bucket.put(key, data, content_type)

    def delete(self, key: str):
        return self._bucket.delete(key)


s3Bucket = S3Bucket()
