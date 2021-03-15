import boto3
import pandas as pd
import sys
from awsglue.utils import getResolvedOptions
import pyarrow
import pkg_resources
env = dict(tuple(str(ws).split()) for ws in pkg_resources.working_set)
print(env)

args = getResolvedOptions(sys.argv, ['bucket', 'prefix'])

client = boto3.client('s3')
s3 = boto3.resource('s3')

bucket=args['bucket']

prefix=args['prefix']
print(bucket, prefix)

for key in client.list_objects(Bucket=bucket, Prefix=prefix)['Contents']:
    print(key['Key'])
    obj_key = key['Key']
    obj = client.get_object(Bucket=bucket, Key=obj_key)
    print(obj)
    body = obj['Body'].read()
    path = f"s3://{bucket}/{obj_key}"
    print(path)
    df = pd.read_parquet(path, engine="pyarrow")
    print(df)
