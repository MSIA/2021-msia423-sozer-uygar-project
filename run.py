import argparse
import logging
import yaml
import os
import json

import pandas as pd

from src.processing.clean import clean
from src.processing.features import generate_train_df
from src.recsys.model import RecipeModel
from src.recsys.evaluate import generate_splits, get_accuracy
from src.upload_data import upload, download
from config.flaskconfig import SQLALCHEMY_DATABASE_URI


# Set logger configuration, prints to stdout
logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s " "%(message)s",
    level=logging.DEBUG,
)

# Only print ERROR statements from S3-related packages
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("aiobotocore").setLevel(logging.ERROR)
logging.getLogger("s3fs").setLevel(logging.ERROR)

# Set logger for this script
logger = logging.getLogger("runner")

if __name__ == "__main__":
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Upload data file to S3 " "or create database"
    )
    subparsers = parser.add_subparsers(dest="subparser_name")

    # Subparser for S3 upload
    sp_upload = subparsers.add_parser(
        "upload", description="Upload data folder to " "specified S3 bucket"
    )
    sp_upload.add_argument("bucket_name", help="Name of S3 bucket")
    sp_upload.add_argument("file_name", help="File name (key)")
    sp_upload.add_argument("data_path", help="Custom path to file")

    # Sub-parser for creating a database
    sp_download = subparsers.add_parser("download", description="Download data stored on AWS S3 to local filesystem")
    sp_download.add_argument("bucket_name", help="Name of S3 bucket")
    sp_download.add_argument("path_from", help="File name (key)")
    sp_download.add_argument("path_to", help="Path to save file")

    sp_pipeline = subparsers.add_parser(
        "pipeline", description="Data processing"
    )
    sp_pipeline.add_argument(
        "step",
        help="Which step to run",
        choices=["clean", "features", "model"],
    )

    sp_pipeline.add_argument("--input", default=None, help="Path to input data")
    sp_pipeline.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to configuration file",
    )
    sp_pipeline.add_argument(
        "--output", "-o", default=None, help="Path to save output CSV"
    )

    args = parser.parse_args()
    logger.info(args)
    # Load configuration file for parameters and tmo path

    sp_used = args.subparser_name

    if sp_used == "upload":
        logger.debug("Upload option invoked")
        upload(args.bucket_name, args.file_name, args.data_path)
    if sp_used == "download":
        logger.debug("Download option invoked")
        download(args.bucket_name, args.path_from, args.path_to)
    elif sp_used == "pipeline":
        # if args.step == "acquire":
        #     # no input, output clouds.data
        #     output = acquire(**config["acquire"]["acquire"])

        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        if args.step == "clean":
            # clouds.data -> clean.csv
            output = clean(args.input, **config["processing"]["clean"])
            logger.info(output)
            logger.info(args.output)
            try:
                if args.output is not None:
                    output.to_csv(args.output, index=False)
            except AttributeError:
                logger.error("Cannot write NoneType to file")

        elif args.step == "features":
            # clean.csv -> full.csv
            input = pd.read_csv(args.input)
            output = generate_train_df(
                input, **config["processing"]["features"]
            )

            if args.output is not None:
                output.to_csv(args.output, index=True)

        elif args.step == "model":
            # full.csv -> features/target -> results in a text file
            train, test = generate_splits(
                args.input, **config["model"]["evaluate"]["splits"]
            )

            output_path = args.output + "/evaluate/"

            if not os.path.isdir(output_path):
                os.mkdir(output_path)

            with open(output_path + "train.json", "w") as f:
                f.write(json.dumps(train))

            with open(output_path + "test.json", "w") as f:
                f.write(json.dumps(test))

            train = clean(
                output_path + "train.json", **config["processing"]["clean"]
            )
            train = generate_train_df(train, **config["processing"]["features"])

            model = RecipeModel(**config["model"]["initialize"])
            model.train(train, **config["model"]["train"])

            acc = get_accuracy(model, test)

            with open(output_path + "result.txt", "w") as f:
                f.write(f"Accuracy: {str(acc)}")

    else:
        parser.print_help()
