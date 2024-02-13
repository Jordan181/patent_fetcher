import responses
import json
import os
import logging

from datetime import date
from unittest import TestCase
from requests import RequestException

from src.fetcher import Fetcher
from src.stores import MemoryPatentStore
from src.models import Patent

class FetcherTest(TestCase):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def setUp(self) -> None:
        self.fetcher = Fetcher(MemoryPatentStore(), rowCount=5)
        logging.disable()

    @responses.activate
    def test_fetcher_retreives_all_patents_in_date_range(self):
        start = "2017-01-01"
        end = "2017-01-03"

        # First request returns page 1
        responses.get(
            url=f"{Fetcher.PATENT_URL}?grantFromDate={start}&grantToDate={end}&start=0&rows=5",
            json=self._json_from_file("patents_1.json"),
        )

        # Second request returns page 2
        responses.get(
            url=f"{Fetcher.PATENT_URL}?grantFromDate={start}&grantToDate={end}&start=5&rows=5",
            json=self._json_from_file("patents_2.json"),
        )

        patents = self._fetch_and_load(start, end)

        self.assertEqual(9, len(patents))
        self.assertEqual(
            Patent(
                patent_number="09532496",
                patent_application_number="US14585764",
                assignee_entity_name="Precision Planting LLC",
                filing_date=date(2014, 12, 30),
                grant_date=date(2017, 1, 3),
                invention_title="Dynamic supplemental downforce control system for planter row units",
            ),
            patents[0]
        )
        self.assertEqual(
            Patent(
                patent_number="09532504",
                patent_application_number="US15065125",
                assignee_entity_name=None,
                filing_date=date(2016, 3, 9),
                grant_date=date(2017, 1, 3),
                invention_title="Control arrangement and method for controlling a position of a transfer device of a harvesting machine",
            ),
            patents[8]
        )

    @responses.activate
    def test_fetcher_does_not_store_data_if_no_patents_in_date_range(self):
        start = "2017-01-05"
        end = "2017-01-06"

        responses.get(
            url=f"{Fetcher.PATENT_URL}?grantFromDate={start}&grantToDate={end}&start=0&rows=5",
            json=self._json_from_file("no_patents.json"),
        )

        patents = self._fetch_and_load(start, end)

        self.assertEqual(0, len(patents))

    @responses.activate
    def test_fetcher_raises_exception_if_response_not_ok(self):
        start = "2017-01-01"
        end = "2017-01-03"

        responses.get(
            url=f"{Fetcher.PATENT_URL}?grantFromDate={start}&grantToDate={end}&start=0&rows=5",
            status=500,
        )

        with self.assertRaises(RequestException):
            self._fetch_and_load(start, end)

    def test_fetcher_raises_value_error_if_end_date_less_than_start(self):
        start = date(2024, 2, 1)
        end = date(2024, 1, 1)

        with self.assertRaises(ValueError):
            self.fetcher.fetch(start, end)

    def _json_from_file(self, filename: str) -> dict:
        with open(os.path.join(self.DATA_DIR, filename)) as f:
            return json.load(f)
        
    def _fetch_and_load(self, start: str, end: str) -> list[Patent]:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)

        self.fetcher.fetch(start_date, end_date)
        
        return self.fetcher.from_store(start_date, end_date)