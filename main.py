import argparse
import os
import logging
import json

from datetime import date

from src.fetcher import Fetcher
from src.models import DataclassJSONEncoder
from src.stores import DatabasePatentStore

def main(start: str, end: str, load: bool):
    logging.basicConfig(level=logging.INFO)

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)

    fetcher = Fetcher(
        DatabasePatentStore(
            host=os.getenv("DB_HOST"),
            name=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT"),
        ),
        certFilePath=os.getenv("USPTO_CERT_FILE_PATH"),
    )
    
    if load:
        patents = fetcher.from_store(start_date, end_date)
        print(json.dumps(patents, indent=4, cls=DataclassJSONEncoder))
    else:
        fetcher.fetch(start_date, end_date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="patent_fetcher",
        description="Fetches patents between a specified date range and stores them in a configured patent store.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "start",
        help="Inclusive start date in ISO format.",
    )
    parser.add_argument(
        "end",
        help="Inclusive end date in ISO format.",
    )
    parser.add_argument(
        "-l",
        "--load",
        action="store_true",
        help="If enabled, load patents from data store instead of fetching from API."
    )

    args = parser.parse_args()

    main(args.start, args.end, args.load)