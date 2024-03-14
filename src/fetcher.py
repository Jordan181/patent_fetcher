import logging
import requests

from collections.abc import Iterator
from datetime import date, datetime

from src.models import Patent
from src.stores import PatentStoreBase


class Fetcher:
    """
    Coordinates process of fetching patent data from USPTO API and storing
    results in an implementation of PatentStoreBase.
    """

    PATENT_URL = "https://developer.uspto.gov/ibd-api/v1/application/grants"
    RESPONSE_DATE_FORMAT = "%m-%d-%Y"
    BUFFER_SIZE = 1000 # Number of patents

    def __init__(
        self,
        store: PatentStoreBase,
        rowStart = 0,
        rowCount = 100,
        certFilePath: str = None
    ) -> None:
        if store is None:
            raise ValueError("Store cannot be None.")
        
        self._store = store
        self._rowStart = rowStart
        self._rowCount = rowCount
        self._certFilePath = certFilePath

    def fetch(self, start: date, end: date) -> None:
        if end < start:
            raise ValueError("End date must be greater than start date.")

        patent_buffer = []
        for patent in self._download(start, end):
            patent_buffer.append(patent)

            if len(patent_buffer) >= self.BUFFER_SIZE:
                self._flush_buffer(patent_buffer)

        self._flush_buffer(patent_buffer)
        logging.info("Complete.")

    def from_store(self, start: date, end: date) -> list[Patent]:
        return self._store.load(start, end)

    def _download(self, start: date, end: date) -> Iterator[Patent]:
        rowStart = self._rowStart
        recordTotalQuantity = None

        logging.info(f"Beginning patent download from {start} to {end}...")

        with requests.session() as session:
            while (
                recordTotalQuantity is None or
                rowStart < recordTotalQuantity
            ):
                response = session.get(
                    url=self.PATENT_URL,
                    params={
                        "grantFromDate": start.isoformat(),
                        "grantToDate": end.isoformat(),
                        "start": rowStart,
                        "rows": self._rowCount,
                    },
                    verify=self._certFilePath,
                )

                if not response.ok:
                    raise requests.RequestException(response=response)
                
                json = response.json()
                results = json["results"]
                recordTotalQuantity = json["recordTotalQuantity"]
                count = 0

                for data in results:
                    yield Patent(
                        patent_number=data["patentNumber"],
                        patent_application_number=data["patentApplicationNumber"],
                        assignee_entity_name=data["assigneeEntityName"],
                        filing_date=self._parse_date(data["filingDate"]),
                        grant_date=self._parse_date(data["grantDate"]),
                        invention_title=data["inventionTitle"],
                    )

                    count += 1
                    logging.info(f"Downloaded patent {count}/{recordTotalQuantity}.")

                rowStart += self._rowCount
        
        logging.info("Download complete.")

    def _flush_buffer(self, patent_buffer: list[Patent]) -> None:
        logging.info("Writing patent data...")
        self._store.save(patent_buffer)
        patent_buffer.clear()
        
    @classmethod
    def _parse_date(cls, date_string: str) -> date:
        return datetime.strptime(date_string, cls.RESPONSE_DATE_FORMAT).date()