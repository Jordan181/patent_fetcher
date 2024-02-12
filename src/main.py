import sys

from datetime import date

from fetcher import Fetcher
from stores import DatabasePatentStore, MemoryPatentStore

def main(from_date: str, to_date: str):
    start = date.fromisoformat(from_date)
    end = date.fromisoformat(to_date)

    fetcher = Fetcher(
        [
            MemoryPatentStore(),
            # DatabasePatentStore(
            #     host=os.getenv("DB_HOST"),
            #     name=os.getenv("DB_NAME"),
            #     user=os.getenv("DB_USER"),
            #     password=os.getenv("DB_PASS"),
            #     port=os.getenv("DB_PORT"),
            # ),
        ]
    )

    fetcher.fetch(start, end)

    print(f"Runing from: {start} to {end}")

if __name__ == "__main__":
    main(*sys.argv[1:])