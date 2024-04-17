import argparse

from concurrent.futures import ThreadPoolExecutor

from upload.upload_nifti import UploadManager



import pathlib
from concurrent.futures import ThreadPoolExecutor
from typing import Union
import botocore.response
from boto3.session import Session
import boto3  # 加载boto3 skd包
import orjson

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', type=str, required=True,
                        help="input rename nifti folder.\r\n")
    parser.add_argument('--work', dest='work', type=int, default=4,
                        help="Process cont max values is 8 .\r\n"
                             "Example: python convert_nifti.py -i input_path -o output_path --work 8")
    return parser.parse_args()


if __name__ == '__main__':
    # args = parse_arguments()
    # upload_manager = UploadManager(args.input)
    # executor = ThreadPoolExecutor(max_workers=args.work)
    # upload_manager.run()
    OBJECT_WEB_URL = 'http://127.0.0.1:9000'
    OBJECT_WEB_access_key = "bHRhU4yBlvx1VkEVhdIC"
    OBJECT_WEB_secret_key = "SyRR1s7WKeav9WFmjtJuwACZNvYcl5S8vryr7uLz"
    OBJECT_BUCKET_NAME = 'test'
    access_key = OBJECT_WEB_access_key
    secret_key = OBJECT_WEB_secret_key
    url = OBJECT_WEB_URL
    bucket_name = OBJECT_BUCKET_NAME
    session = Session(access_key, secret_key)
    s3_client = session.client('s3', endpoint_url=url, verify=False)
    response = s3_client.list_objects(Bucket=OBJECT_BUCKET_NAME,)
    # print(response.keys())
    # print(response['Contents'])
    print(response['Contents'][0])