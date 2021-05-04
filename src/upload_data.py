import boto3

def upload(bucketname, filename, datapath):

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucketname)

    bucket.upload_file(datapath, filename)