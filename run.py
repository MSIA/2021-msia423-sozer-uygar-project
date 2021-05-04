import argparse
from pathlib import Path

from src.upload_data import upload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Upload data folder to specified S3 bucket")
    parser.add_argument("BUCKETNAME", help = "Name of S3 bucket")
    parser.add_argument("FILENAME", help = "File name (key)")
    
    parser.add_argument("-d", "--DATAPATH", default="data/train.json", \
                                            help = "Custom path to file", \
                                            metavar= "") 

    args = parser.parse_args()

    upload(args.BUCKETNAME, args.FILENAME, args.DATAPATH)
