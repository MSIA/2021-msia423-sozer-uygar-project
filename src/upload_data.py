import logging

import boto3

logger = logging.getLogger(__name__)


def upload(bucketname, filename, datapath):
    """Upload a specified data file to an S3 bucket

    Args:
        bucketname (String): Name of S3 bucket (do not include 'S3://')
        filename (String): Desired name of file
        datapath (String): Location of the data file on local
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucketname)

    # Upload file to S3
    try:
        bucket.upload_file(datapath, filename)
    except boto3.exceptions.S3UploadFailedError:
        logger.error("Bucket does not exist")
    except FileNotFoundError:
        logger.error("File does not exist on the specified path")
