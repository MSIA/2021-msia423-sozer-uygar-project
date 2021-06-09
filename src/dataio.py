import logging
import re

import boto3
from botocore.exceptions import NoCredentialsError

logger = logging.getLogger(__name__)


def parse_s3(s3path):
    """Parses a raw S3 path to extract bucket name and
    file path on cloud

    Args:
        s3path (str): Raw S3 path to file

    Returns:
        str, str: Bucket name and file path
    """
    try:
        regex = r"s3://([\w._-]+)/([\w./_-]+)"

        m = re.match(regex, s3path)
        s3bucket = m.group(1)
        s3path = m.group(2)
    except TypeError:
        logger.error("invalid type URI provided for S3")
        return None, None

    return s3bucket, s3path


def upload(bucketname, filename, datapath):
    """Upload a specified data file to an S3 bucket

    Args:
        bucketname (String): Name of S3 bucket (do not include 'S3://')
        filename (String): Desired name of file
        datapath (String): Location of the data file on local
    """

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucketname)
    logger.info("Currently connected to %s", bucketname)

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


def download(bucketname=None, path_from=None, path_to=None, s3path=None):
    """Download a file from S3

    Args:
        bucketname (String): name of bucket
        path_from (String): S3 path to file (omit S3://)
        path_to (String): local path to copy file to
    """
    if s3path:
        bucketname, path_from = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucketname)
    logger.info("Currently connected to %s", bucketname)

    # Download file from S3
    try:
        bucket.download_file(path_from, path_to)
        logger.info("Successfully downloaded file, %s", path_from)
    except FileNotFoundError:
        logger.error("File does not exist on the specified path")
    except NoCredentialsError:
        logger.error("AWS credentials not set as env variables")
