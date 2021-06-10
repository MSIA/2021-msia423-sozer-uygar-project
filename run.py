import argparse
import logging
import yaml
import os
import json

import pandas as pd

from src.data_model import create_db
from src.processing.clean import clean, convert_json
from src.processing.features import generate_train_df
from src.recsys.model import RecipeModel
from src.recsys.evaluate import generate_splits, get_accuracy
from src.dataio import upload, download
from config.flaskconfig import SQLALCHEMY_DATABASE_URI


# Set logger configuration, prints to stdout
logging.basicConfig(
    format="%(asctime)s %(name)-30s %(levelname)-8s " "%(message)s",
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
        description="CuisineHelpr CLI - upload data file, run model pipeline,\
            run web application"
    )
    subparsers = parser.add_subparsers(dest="subparser_name")

    # Subparser for S3 upload
    sp_upload = subparsers.add_parser(
        "upload", description="Upload data folder to specified S3 bucket"
    )
    sp_upload.add_argument(
        "--bucket_name", default=None, help="Name of S3 bucket"
    )
    sp_upload.add_argument("--file_name", default=None, help="File name (key)")
    sp_upload.add_argument(
        "--data_path", default=None, help="Custom path to file"
    )

    # Sub-parser for creating a database
    sp_download = subparsers.add_parser(
        "download",
        description="Download data stored on AWS S3 to local filesystem",
    )
    sp_download.add_argument("--bucket_name", help="Name of S3 bucket")
    sp_download.add_argument("--path_from", help="File name (key)")
    sp_download.add_argument("--path_to", help="Path to save file")
    sp_download.add_argument("--s3path", default=None, help="Raw path to S3")

    sp_create = subparsers.add_parser(
        "create", description="Create database locally or on AWS"
    )
    sp_create.add_argument("--sqlalchemy_uri", default=SQLALCHEMY_DATABASE_URI)

    # Entire pipeline step
    sp_pipeline = subparsers.add_parser(
        "pipeline", description="Data processing"
    )
    sp_pipeline.add_argument(
        "step",
        help="Which step to run",
        choices=["clean", "features", "model"],
    )

    # Input, output, config arguments for model pipeline
    sp_pipeline.add_argument(
        "--input", default=None, help="Path to input data"
    )
    sp_pipeline.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to configuration file",
    )
    sp_pipeline.add_argument(
        "--output", "-o", default=None, help="Path to save output CSV"
    )

    args = parser.parse_args()
    # Load configuration file for parameters and tmo path

    sp_used = args.subparser_name

    if sp_used == "upload":
        logger.debug("Upload option invoked")
        upload(args.bucket_name, args.file_name, args.data_path)
    elif sp_used == "download":
        logger.debug("Download option invoked")
        download(s3path=args.s3path, path_to=args.path_to)
    elif sp_used == "create":
        logger.debug("Create database")
        create_db(args.sqlalchemy_uri)
    elif sp_used == "pipeline":

        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        if args.step == "clean":
            logger.debug("Attempting clean")
            # clouds.data -> clean.csv
            data_dict = convert_json(args.input)
            output = clean(data_dict, **config["processing"]["clean"])
            logger.info("Successfully cleaned input file %s, attempting save")
            try:
                if args.output is not None:
                    output.to_csv(args.output, index=False)
                    logger.info(
                        "Successfully saved file to output \
                        path %s",
                        args.output,
                    )
            except AttributeError:
                logger.error("Cannot write NoneType to file")

        elif args.step == "features":
            # clean.csv -> full.csv
            logger.info("Preparing cleaned dataset for training")
            input = pd.read_csv(args.input)
            output = generate_train_df(
                input, **config["processing"]["features"]
            )
            logger.info(
                "Successfully completed training set generation\
                 from input %s",
                args.input,
            )

            if args.output is not None:
                output.to_csv(args.output, index=True)
                logger.info(
                    "Successfully saved file to output \
                    path %s",
                    args.output,
                )

        elif args.step == "model":
            # full.csv -> features/target -> results in a text file
            logger.info("Generating train-test split")
            train, test = generate_splits(
                args.input, **config["model"]["evaluate"]["splits"]
            )
            logger.info("Created train-test split")

            output_path = (
                args.output + config["model"]["evaluate"]["evaluate_dir"]
            )

            # Create evaluation path
            if not os.path.isdir(output_path):
                os.mkdir(output_path)

            # Save training set
            with open(
                output_path + config["model"]["evaluate"]["trainset_path"], "w"
            ) as f:
                f.write(json.dumps(train))
                logger.info("Saving training set to %s", output_path)

            # Save test set
            with open(
                output_path + config["model"]["evaluate"]["testset_path"], "w"
            ) as f:
                f.write(json.dumps(test))
                logger.info("Saving test set to %s", output_path)

            # Clean & featurize training set
            data_dict = convert_json(
                output_path + config["model"]["evaluate"]["trainset_path"]
            )
            train = clean(
                data_dict,
                **config["processing"]["clean"],
            )
            train = generate_train_df(
                train, **config["processing"]["features"]
            )

            # Create and train model
            model = RecipeModel(**config["model"]["initialize"])
            model.train(train, **config["model"]["train"])

            # Calculate accuracy
            acc = get_accuracy(model, test)

            # Write results to file
            with open(
                output_path + config["model"]["evaluate"]["result_path"], "w"
            ) as f:
                f.write(f"Accuracy: {str(acc)}")
                logger.info("Saving results file at %s", output_path)

    else:
        parser.print_help()
