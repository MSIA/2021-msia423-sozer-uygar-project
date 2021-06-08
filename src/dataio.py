import logging

import boto3
from botocore.exceptions import NoCredentialsError

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
        logger.info("Successfully uploaded file")
    except boto3.exceptions.S3UploadFailedError:
        logger.error("Bucket does not exist")
    except FileNotFoundError:
        logger.error("File does not exist on the specified local path")
    except NoCredentialsError:
        logger.error("AWS credentials not set as env variables")


def download(bucketname, path_from, path_to):
    """Download a file from S3

    Args:
        bucketname (String): name of bucket
        path_from (String): S3 path to file (omit S3://)
        path_to (String): local path to copy file to
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucketname)

    # Download file from S3
    try:
        bucket.download_file(path_from, path_to)
        logger.info("Successfully downloaded file, %s", path_from)
    except FileNotFoundError:
        logger.error("File does not exist on the specified path")
    except NoCredentialsError:
        logger.error("AWS credentials not set as env variables")
