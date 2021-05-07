import argparse
import logging

from src.upload_data import upload
from src.data_model import create_db
from config.dbconfig import SQLALCHEMY_DATABASE_URI, DATA_PATH

logger = logging.getLogger("runner")


if __name__ == "__main__":
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Upload data file to S3 "
                                                 "or create database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Subparser for S3 upload
    sp_upload = subparsers.add_parser("upload",
                                      description="Upload data folder to "
                                                  "specified S3 bucket")
    sp_upload.add_argument("bucket_name", help="Name of S3 bucket")
    sp_upload.add_argument("file_name", help="File name (key)")
    sp_upload.add_argument("-d", "--data_path",
                           default=DATA_PATH,
                           help="Custom path to file",
                           metavar="")

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create", description="Create database")
    sb_create.add_argument("-e", "--engine_string",
                           default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database",
                           metavar="")

    args = parser.parse_args()
    sp_used = args.subparser_name
    
    if sp_used == 'create':
        logger.debug("Create option invoked")
        create_db(args.engine_string)
    elif sp_used == 'upload':
        logger.debug("Upload option invoked")
        upload(args.bucket_name, args.file_name, args.data_path)
    else:
        parser.print_help()
