import os

from datetime import date
from unittest import TestCase

from src.models import Patent
from src.stores import DatabasePatentStore

class DatabasePatentStoreTest(TestCase):
    def setUp(self) -> None:
        self.store = DatabasePatentStore(
            host=os.getenv("DB_HOST"),
            name=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT"),
        )

    def tearDown(self) -> None:
        self.store.clear()

    def test_load_returns_empty_list_if_no_patents_saved(self):
        patents = self.store.load(date(1970, 1, 1), date.today())
        self.assertEqual(0, len(patents))

    def test_can_save_and_load_patents(self):
        source_patents = [
            Patent("1", "2", "My Entity", date(2024, 2, 10), date(2024, 2, 13), "My Invention"),
            Patent("3", "4", "My Entity 2", date(2024, 2, 11), date(2024, 2, 14), "My Invention 2"),
        ]

        self.store.save(source_patents)

        loaded_patents = self.store.load(date(2024, 2, 13), date(2024, 2, 14))

        self.assertListEqual(source_patents, loaded_patents)

    def test_saving_duplicate_records_does_nothing(self):
        source_patents = [
            Patent("1", "2", "My Entity", date(2024, 2, 10), date(2024, 2, 13), "My Invention"),
            Patent("3", "4", "My Entity 2", date(2024, 2, 11), date(2024, 2, 14), "My Invention 2"),
        ]

        # Try saving the same patent data twice
        self.store.save(source_patents)
        self.store.save(source_patents)

        loaded_patents = self.store.load(date(2024, 2, 13), date(2024, 2, 14))

        self.assertListEqual(source_patents, loaded_patents)

    def test_load_only_returns_records_with_grant_date_between_range(self):
        source_patents = [
            Patent("1", "2", "My Entity", date(2024, 2, 10), date(2024, 2, 13), "My Invention"),
            Patent("3", "4", "My Entity 2", date(2024, 2, 11), date(2024, 2, 15), "My Invention 2"),
        ]

        self.store.save(source_patents)

        loaded_patents = self.store.load(date(2024, 2, 13), date(2024, 2, 14))

        self.assertEqual(1, len(loaded_patents))
        self.assertEqual(source_patents[0], loaded_patents[0])
