import logging
import os
import uuid
from concurrent import futures

import boto3
from boto3_type_annotations.s3 import Client
from botocore.response import StreamingBody

from singleton import Singleton


class S3Bucket(metaclass=Singleton):
    def __init__(self):
        aws_access_key = os.getenv("AWS_ACCESS_KEY")
        aws_secret_key = os.getenv("AWS_SECRET_KEY")
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")

        self.client: Client = boto3.client(
            's3',
            region_name="eu-central-1",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

    def get(self, key: str, folder_prefix: str = ""):
        return self.fetch(folder_prefix + key)

    def upload(self, data: bytes, key: str = None, folder_prefix: str = "", content_type: str = "image/png"):
        if key is None:
            key = str(uuid.uuid4())

        try:
            self.client.put_object(Key=folder_prefix + key, Bucket=self.bucket_name, Body=data, ContentType=content_type)
        except Exception as e:
            raise e

    def delete(self, key: str, folder_prefix: str = ""):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=folder_prefix + key)
        except Exception as e:
            raise e

    def fetch(self, key):
        try:
            res: StreamingBody = self.client.get_object(Bucket=self.bucket_name, Key=key)["Body"]
            return res.read()
        except Exception as e:
            print(f"error accessing {key}")
            raise e

    def fetch_all(self, keys):
        print('wat')
        keys = list(keys)
        with futures.ProcessPoolExecutor(max_workers=5) as executor:
            print("pre sub", keys)
            future_to_key = {executor.submit(self.fetch, key): key for key in keys}

            print("All URLs submitted.")

            for future in futures.as_completed(future_to_key):

                key = future_to_key[future]
                exception = future.exception()

                if not exception:
                    yield key, future.result()
                else:
                    yield key, exception


s3Bucket = S3Bucket()
